import React, { useState } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const UploadForm = ({ onFilesSelect, multiple = false }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    updateFiles(selectedFiles);
  };

  const updateFiles = (newFiles) => {
    const validFiles = newFiles.filter(file => file.type === 'application/pdf');
    const updatedFiles = multiple ? [...files, ...validFiles] : validFiles;
    setFiles(updatedFiles);
    onFilesSelect(updatedFiles);
  };

  const removeFile = (index) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    onFilesSelect(updatedFiles);
  };

  return (
    <div className="w-full">
      <div
        className={twMerge(
          "relative border-2 border-dashed rounded-2xl p-8 transition-all duration-300 flex flex-col items-center justify-center min-h-[200px] cursor-pointer",
          isDragging ? "border-primary-500 bg-primary-500/10" : "border-slate-700 hover:border-slate-500 bg-slate-800/20"
        )}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          updateFiles(Array.from(e.dataTransfer.files));
        }}
        onClick={() => document.getElementById('file-upload').click()}
      >
        <input
          id="file-upload"
          type="file"
          className="hidden"
          accept=".pdf"
          onChange={handleFileChange}
          multiple={multiple}
        />
        
        <div className="bg-primary-500/10 p-4 rounded-full mb-4">
          <Upload className="w-8 h-8 text-primary-400" />
        </div>
        
        <p className="text-lg font-medium text-slate-200">
          Click to upload or drag and drop
        </p>
        <p className="text-sm text-slate-400 mt-1">
          Supported format: PDF (Max 10MB)
        </p>
      </div>

      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between bg-slate-800/40 p-3 rounded-xl border border-slate-700 animate-slide-up">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary-400" />
                <span className="text-sm font-medium truncate max-w-[200px]">{file.name}</span>
              </div>
              <button onClick={(e) => { e.stopPropagation(); removeFile(index); }} className="text-slate-500 hover:text-red-400">
                <X className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadForm;
