import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { CreatePlan } from './pages/CreatePlan';
import { PlanDetails } from './pages/PlanDetails';
import { VersionSnapshot } from './pages/VersionSnapshot';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="plans/new" element={<CreatePlan />} />
          <Route path="plans/:id" element={<PlanDetails />} />
          <Route path="plans/:id/versions/:version" element={<VersionSnapshot />} />
        </Route>
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
        toastClassName="bg-slate-900 border border-slate-800 text-slate-200 shadow-xl rounded-lg"
      />
    </BrowserRouter>
  );
};

export default App;
