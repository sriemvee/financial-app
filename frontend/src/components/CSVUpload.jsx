import React, { useState } from 'react';
import { uploadCSV } from '../utils/api';

const CSVUpload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const result = await uploadCSV(formData);
      setMessage(`✓ Imported ${result.imported_count} expenses`);
      onSuccess(result);
      setFile(null);
    } catch (error) {
      setMessage(`✗ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="border-2 border-dashed border-gray-300 rounded p-6 text-center">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="hidden"
          id="csv-input"
        />
        <label htmlFor="csv-input" className="cursor-pointer">
          {file ? (
            <p className="text-green-600 font-semibold">{file.name}</p>
          ) : (
            <p className="text-gray-600">Click to upload CSV or drag & drop</p>
          )}
        </label>
      </div>
      <button
        type="submit"
        disabled={!file || loading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Uploading...' : 'Upload & Import'}
      </button>
      {message && <p className="text-sm text-center">{message}</p>}
    </form>
  );
};

export default CSVUpload;