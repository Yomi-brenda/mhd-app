// import React from 'react';
// import { Link } from 'react-router-dom';

// const Navbar = ({ token, onLogout }) => {
//   return (
//     <nav className="navbar">
//       <div className="navbar-container">
//         <Link to="/" className="navbar-brand">Auth App</Link>
//         <div className="navbar-links">
//           {!token ? (
//             <>
//               <Link to="/">Login</Link>
//               <Link to="/register">Register</Link>
//             </>
//           ) : (
//             <>
//               <Link to="/dashboard">Dashboard</Link>
//               <button onClick={onLogout}>Logout</button>
//             </>
//           )}
//         </div>
//       </div>
//     </nav>
//   );
// };

// export default Navbar;

import React from 'react';
import styled from 'styled-components';

const Nav = styled.nav`
  background: #2563eb;
  padding: 1rem;
  color: white;
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
`;

const Navbar = ({ token, onLogout }) => (
  <Nav>
    <span>ZEN</span>
    {token && (
      <LogoutButton onClick={onLogout}>Logout</LogoutButton>
    )}
  </Nav>
);

export default Navbar;