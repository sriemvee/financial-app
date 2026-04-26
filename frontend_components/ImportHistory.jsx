import React from 'react';

const ImportHistory = ({ history }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Import History</h2>
      {history.length === 0 ? (
        <p className="text-gray-500 text-sm">No imports yet</p>
      ) : (
        <div className="space-y-3">
          {history.map((item, index) => (
            <div key={index} className="border rounded p-3 text-sm">
              <p className="font-semibold">Batch {index + 1}</p>
              <p className="text-gray-600">Imported: {item.imported_count}</p>
              <p className="text-gray-600">Skipped: {item.skipped_count}</p>
              <p className="text-gray-600">Duplicates: {item.duplicates_found}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ImportHistory;