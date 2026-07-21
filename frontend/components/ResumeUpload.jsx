import { useRef, useState } from "react";

export default function ResumeUpload({ onFileSelected, fileName }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = (files) => {
    if (files && files[0]) onFileSelected(files[0]);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={`cursor-pointer rounded-xl border-2 border-dashed px-6 py-10 text-center transition
        ${dragOver ? "border-accent bg-accent/5" : "border-black/15 bg-white"}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {fileName ? (
        <p className="text-sm font-medium text-ink">{fileName} selected</p>
      ) : (
        <>
          <p className="text-sm font-medium text-ink">
            Drop your resume here, or click to browse
          </p>
          <p className="mt-1 text-xs text-ink/50">PDF or plain text</p>
        </>
      )}
    </div>
  );
}
