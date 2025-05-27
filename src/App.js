// import React, { useState } from 'react';
// import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
// import Register from './components/Register';
// import Login from './components/Login';
// import Dashboard from './components/Dashboard';
// import Navbar from './components/Navbar';

// function App() {
//   const [token, setToken] = useState(localStorage.getItem('token') || '');

//   const handleLogout = () => {
//     localStorage.removeItem('token');
//     setToken('');
//   };

//   return (
//     <Router>
//       <div style={{ minHeight: '100vh' }}> {/* Replaced bg-gray-100 */}
//         <Navbar token={token} onLogout={handleLogout} />
//         <Switch>
//           <Route exact path="/">
//             <Login setToken={setToken} />
//           </Route>
//           <Route path="/register">
//             <Register />
//           </Route>
//           <Route path="/dashboard">
//             <Dashboard token={token} />
//           </Route>
//         </Switch>
//       </div>
//     </Router>
//   );
// }

// export default App;

import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, useLocation, Redirect } from 'react-router-dom';
import HomePage from './components/HomePage';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';
import ResourcesPage from './components/ResourcesPage';


const App = () => {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      {location.pathname === '/dashboard' && <Navbar token={token} onLogout={handleLogout} />}
      <Switch>
        <Route exact path="/"><HomePage />   </Route>
        <Route path="/login">
          <Login setToken={setToken} />
        </Route>
        <Route path="/register">
          <Register />
        </Route>
        <Route path="/dashboard">
          <Dashboard token={token} />
        </Route>
        <Route exact path="/resources" component={ResourcesPage} />
        <Redirect to="/login" />

      </Switch>
    </div>
  );
};

// Wrap App with Router since useLocation requires Router context
const AppWithRouter = () => (
  <Router>
    <App />
  </Router>
);

export default AppWithRouter;