import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./pages/Login"
import Products from "./pages/Products"
import Orders from "./pages/Orders"

function App() {
  return (
    <BrowserRouter>

      <div className="layout">

        <header className="header">
          <h1>Online Shop</h1>
        </header>

        <main className="main">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/products" element={<Products />} />
            <Route path="/orders" element={<Orders />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>© 2026 Online Shop</p>
        </footer>

      </div>

    </BrowserRouter>
  )
}

export default App