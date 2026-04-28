import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import Summary from './pages/Summary';
import Import from './pages/Import';
import Income from './pages/Income';
import Sources from './pages/Sources';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/summary" element={<Summary />} />
          <Route path="/import" element={<Import />} />
          <Route path="/income" element={<Income />} />
          <Route path="/sources" element={<Sources />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
