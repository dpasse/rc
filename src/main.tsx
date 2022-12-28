import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

const element = document.getElementById('rc-app') as HTMLElement;
const root = createRoot(element);

root.render(
  <StrictMode>
    <p>Hi!</p>
  </StrictMode>,
);