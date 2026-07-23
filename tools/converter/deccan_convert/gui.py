"""tkinter GUI — the default mode when the app is launched with no arguments.

Single window: input picker, matrix-filtered output format, document-detail
fields (auto-filled from the input, user-overridable), output path, convert
button with progress bar, and a status log. Conversion runs on a worker
thread; results come back through a queue so the UI never freezes during a
PDF render.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from deccan_convert import __version__, matrix
from deccan_convert.convert import ConversionResult, convert, extract_metadata
from deccan_convert.ir import CLASSIFICATIONS, DOCUMENT_TYPES, Metadata

_FILETYPES = [
    ("All supported", "*.md *.markdown *.html *.htm *.docx *.xlsx *.pptx *.pdf"),
    ("Markdown", "*.md *.markdown"),
    ("HTML", "*.html *.htm"),
    ("Word document", "*.docx"),
    ("Excel workbook", "*.xlsx"),
    ("PowerPoint deck", "*.pptx"),
    ("PDF", "*.pdf"),
]

_FORMAT_LABELS = {
    "md": "Markdown (.md)",
    "html": "HTML (.html)",
    "docx": "Word (.docx)",
    "pdf": "PDF (.pdf)",
    "xlsx": "Excel (.xlsx)",
    "pptx": "PowerPoint (.pptx)",
}
_LABEL_FORMATS = {v: k for k, v in _FORMAT_LABELS.items()}


class ConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"Deccan Convert — deccan-design v2.0 ({__version__})")
        root.minsize(600, 560)
        self.queue: queue.Queue = queue.Queue()
        self.working = False

        pad = {"padx": 10, "pady": 4}
        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        # --- input row ---
        ttk.Label(frame, text="Input file").grid(row=0, column=0, sticky="w", **pad)
        self.input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.input_var, state="readonly").grid(
            row=0, column=1, sticky="ew", **pad
        )
        ttk.Button(frame, text="Choose file…", command=self.pick_input).grid(
            row=0, column=2, **pad
        )

        # --- output format ---
        ttk.Label(frame, text="Convert to").grid(row=1, column=0, sticky="w", **pad)
        self.format_var = tk.StringVar()
        self.format_box = ttk.Combobox(
            frame, textvariable=self.format_var, state="disabled", values=[]
        )
        self.format_box.grid(row=1, column=1, sticky="ew", **pad)
        self.format_box.bind("<<ComboboxSelected>>", lambda _e: self.on_format_change())
        self.hint_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.hint_var, foreground="#78716C").grid(
            row=2, column=1, columnspan=2, sticky="w", padx=10
        )

        # --- document details ---
        self.details = ttk.LabelFrame(frame, text="Document details", padding=8)
        self.details.grid(row=3, column=0, columnspan=3, sticky="ew", **pad)
        self.details.columnconfigure(1, weight=1)
        self.meta_vars: dict[str, tk.StringVar] = {}
        self._detail_row(0, "Title *", "title")
        self._detail_row(1, "Subtitle", "subtitle")
        self._detail_combo(2, "Document type *", "document_type", DOCUMENT_TYPES)
        self._detail_row(3, "Prepared by *", "prepared_by")
        self._detail_row(4, "Date", "date")
        self._detail_row(5, "Version", "version")
        self._detail_combo(6, "Classification", "classification", CLASSIFICATIONS)

        ttk.Label(self.details, text="Word template").grid(
            row=7, column=0, sticky="w", padx=4, pady=2
        )
        self.template_var = tk.StringVar(value="document")
        self.template_box = ttk.Combobox(
            self.details, textvariable=self.template_var, state="disabled",
            values=["document", "technical-spec", "policy", "customer-letter"],
        )
        self.template_box.grid(row=7, column=1, sticky="ew", padx=4, pady=2)

        self.logo_var = tk.BooleanVar(value=False)
        self.logo_check = ttk.Checkbutton(
            self.details, text="Use graphical logo on cover", variable=self.logo_var
        )
        self.logo_check.grid(row=8, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        # --- output path ---
        ttk.Label(frame, text="Save as").grid(row=4, column=0, sticky="w", **pad)
        self.output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_var).grid(
            row=4, column=1, sticky="ew", **pad
        )
        ttk.Button(frame, text="Browse…", command=self.pick_output).grid(
            row=4, column=2, **pad
        )

        # --- convert + progress ---
        self.convert_btn = ttk.Button(
            frame, text="Convert", command=self.start_conversion, state="disabled"
        )
        self.convert_btn.grid(row=5, column=0, columnspan=2, sticky="ew", **pad)
        ttk.Button(frame, text="Export design kit…", command=self.export_kit).grid(
            row=5, column=2, sticky="ew", **pad
        )
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10)

        # --- status log ---
        self.status = tk.Text(frame, height=9, state="disabled", wrap="word")
        self.status.grid(row=7, column=0, columnspan=3, sticky="nsew", **pad)
        frame.rowconfigure(7, weight=1)
        self.status.tag_configure("error", foreground="#B91C1C")
        self.status.tag_configure("warning", foreground="#92400E")

        self.log(
            "Select a file to convert. Google Docs/Sheets/Slides: download as "
            ".docx/.xlsx/.pptx first (File > Download), convert, then re-upload "
            "to Drive."
        )
        self.root.after(150, self._poll_queue)

    # --- widget helpers ---

    def _detail_row(self, row: int, label: str, field: str) -> None:
        ttk.Label(self.details, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
        var = tk.StringVar()
        self.meta_vars[field] = var
        ttk.Entry(self.details, textvariable=var).grid(
            row=row, column=1, sticky="ew", padx=4, pady=2
        )

    def _detail_combo(self, row: int, label: str, field: str, values) -> None:
        ttk.Label(self.details, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
        var = tk.StringVar()
        self.meta_vars[field] = var
        ttk.Combobox(self.details, textvariable=var, values=list(values)).grid(
            row=row, column=1, sticky="ew", padx=4, pady=2
        )

    def log(self, message: str, tag: str = "") -> None:
        self.status.configure(state="normal")
        self.status.insert("end", message + "\n", tag or ())
        self.status.see("end")
        self.status.configure(state="disabled")

    # --- interactions ---

    def pick_input(self) -> None:
        chosen = filedialog.askopenfilename(filetypes=_FILETYPES)
        if not chosen:
            return
        self.input_var.set(chosen)
        path = Path(chosen)
        try:
            fmt = matrix.detect_format(path)
        except matrix.UnsupportedConversion as exc:
            self.log(str(exc), "error")
            return

        outputs = matrix.outputs_for(fmt)
        labels = [_FORMAT_LABELS[f] for f in outputs]
        self.format_box.configure(state="readonly", values=labels)
        self.format_var.set(labels[0])
        if fmt in ("xlsx", "pptx"):
            self.hint_var.set(
                "Spreadsheets and decks restyle to their own format. For PDF, "
                "open the result in Office and use File > Export."
            )
        elif fmt == "pdf":
            self.hint_var.set(
                "PDF input is text extraction only — images and exact styling "
                "are not preserved."
            )
        else:
            self.hint_var.set("")

        self._set_details_enabled(fmt in matrix.DOCUMENT_FORMATS)
        if fmt in matrix.DOCUMENT_FORMATS:
            try:
                meta = extract_metadata(path)
            except Exception as exc:
                self.log(f"Could not read metadata: {exc}", "warning")
                meta = Metadata()
            defaults = meta.with_defaults()
            for f in ("title", "subtitle", "document_type", "prepared_by"):
                self.meta_vars[f].set(getattr(meta, f))
            for f in ("date", "version", "classification"):
                self.meta_vars[f].set(getattr(defaults, f))

        self.on_format_change()
        self.convert_btn.configure(state="normal")

    def on_format_change(self) -> None:
        if not self.input_var.get() or not self.format_var.get():
            return
        fmt = _LABEL_FORMATS[self.format_var.get()]
        self.output_var.set(
            str(matrix.default_output_path(Path(self.input_var.get()), fmt))
        )
        in_fmt = matrix.detect_format(Path(self.input_var.get()))
        self._set_details_enabled(in_fmt in matrix.DOCUMENT_FORMATS)
        # Template flavors apply to Word output only; the logo option applies
        # to any format with a cover (everything except md and xlsx).
        self.template_box.configure(state="readonly" if fmt == "docx" else "disabled")
        if fmt != "docx":
            self.template_var.set("document")
        self.logo_check.configure(
            state="normal" if fmt in ("html", "pdf", "docx", "pptx") else "disabled"
        )

    def _set_details_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for child in self.details.winfo_children():
            child.configure(state=state)

    def pick_output(self) -> None:
        if not self.format_var.get():
            return
        fmt = _LABEL_FORMATS[self.format_var.get()]
        ext = matrix.default_extension(fmt)
        chosen = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=Path(self.output_var.get()).name if self.output_var.get() else "",
            filetypes=[(_FORMAT_LABELS[fmt], f"*{ext}")],
        )
        if chosen:
            self.output_var.set(chosen)

    def start_conversion(self) -> None:
        if self.working:
            return
        input_path = Path(self.input_var.get())
        output_path = Path(self.output_var.get())
        in_fmt = matrix.detect_format(input_path)

        metadata = None
        if in_fmt in matrix.DOCUMENT_FORMATS:
            metadata = Metadata(**{f: v.get().strip() for f, v in self.meta_vars.items()})
            missing = metadata.missing_required()
            if missing:
                self.log(
                    "Fill in the required fields first: " + ", ".join(missing),
                    "error",
                )
                return

        self.working = True
        self.convert_btn.configure(state="disabled")
        self.progress.start(12)
        template = self.template_var.get() or "document"
        logo = bool(self.logo_var.get())
        thread = threading.Thread(
            target=self._worker,
            args=(input_path, output_path, metadata, template, logo),
            daemon=True,
        )
        thread.start()

    def _worker(self, input_path: Path, output_path: Path, metadata, template, logo) -> None:
        try:
            result = convert(
                input_path,
                output_path,
                metadata=metadata,
                log=lambda msg: self.queue.put(("log", msg)),
                template=template,
                logo=logo,
            )
            self.queue.put(("done", result))
        except Exception as exc:
            self.queue.put(("error", f"{exc}"))

    def export_kit(self) -> None:
        chosen = filedialog.askdirectory(title="Export design kit to…")
        if not chosen:
            return
        from deccan_convert.kit import export_kit

        try:
            target = export_kit(Path(chosen))
        except (FileNotFoundError, FileExistsError, OSError) as exc:
            self.log(f"Export failed: {exc}", "error")
            return
        self.log(f"Design kit written to {target}")

    def _poll_queue(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "log":
                    self.log(payload)
                elif kind == "error":
                    self.log(f"Error: {payload}", "error")
                    self._finish()
                elif kind == "done":
                    result: ConversionResult = payload
                    for warning in result.warnings:
                        self.log(f"Warning: {warning}", "warning")
                    self.log(f"Done: {result.output_path}")
                    self._finish()
        except queue.Empty:
            pass
        self.root.after(150, self._poll_queue)

    def _finish(self) -> None:
        self.working = False
        self.progress.stop()
        self.convert_btn.configure(state="normal")


def run_gui() -> int:
    root = tk.Tk()
    try:
        # Native themes on Windows/macOS; 'clam' beats the dated default on X11.
        if root.tk.call("tk", "windowingsystem") == "x11":
            ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    ConverterApp(root)
    root.mainloop()
    return 0
