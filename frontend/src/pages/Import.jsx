import React, { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { formatDate } from '../utils/formatting';

const Import = () => {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const data = await api.getImportBatches();
      setBatches(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file');
      return;
    }

    try {
      setUploading(true);
      await api.uploadCSV(file);
      setFile(null);
      fetchBatches();
      alert('CSV uploaded successfully!');
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteBatch = async (id) => {
    if (!window.confirm('Are you sure? This will delete all expenses in this batch.')) return;
    try {
      await api.deleteImportBatch(id);
      fetchBatches();
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">CSV Import</h1>

      {/* Upload Form */}
      <div className="bg-blue-50 p-6 rounded-lg mb-8 border-2 border-blue-200">
        <h2 className="text-lg font-semibold mb-4">Upload CSV File</h2>
        <form onSubmit={handleUpload} className="flex gap-4">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={uploading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
        <p className="text-sm text-gray-600 mt-2">
          Upload bank statements or credit card CSV files. Required columns: date, amount, description
        </p>
      </div>

      {/* Import Batches */}
      {error ? (
        <div className="text-red-600">Error: {error}</div>
      ) : (
        <div>
          <h2 className="text-lg font-semibold mb-4">Import History</h2>
          {batches && batches.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100 border">
                    <th className="border p-3 text-left">Batch ID</th>
                    <th className="border p-3 text-left">Source</th>
                    <th className="border p-3 text-left">Imported At</th>
                    <th className="border p-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {batches.map((batch) => (
                    <tr key={batch.id} className="border hover:bg-gray-50">
                      <td className="border p-3">#{batch.id}</td>
                      <td className="border p-3">{batch.source_name}</td>
                      <td className="border p-3">{formatDate(batch.imported_at)}</td>
                      <td className="border p-3 text-center">
                        <button
                          onClick={() => handleDeleteBatch(batch.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-600">No import batches yet.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Import;
