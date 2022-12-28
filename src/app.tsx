import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { HomePage } from './components/home/HomePage';
import { NotFoundPage } from './components/errors/NotFoundPage';

import './scss/styles.scss';

const element = document.getElementById('app') as HTMLElement;
const root = createRoot(element);

root.render(
  <StrictMode>
    <Router>
      <Routes>
        <Route index={true} element={<HomePage />} />
        <Route path="*" element={ <NotFoundPage /> } />
      </Routes>
    </Router>
  </StrictMode>,
);