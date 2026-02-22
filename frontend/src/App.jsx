/**
 * MindCare AI - Main Application Component
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, Users, UserPlus, LayoutDashboard } from 'lucide-react';

// Pages
import PatientIntake from './pages/PatientIntake';
import AdminDashboard from './pages/AdminDashboard';
import TherapistDashboard from './pages/TherapistDashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/20 to-neutral-50">
        {/* Navigation Header */}
        <nav className="bg-white/80 backdrop-blur-md shadow-sm border-b border-neutral-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              {/* Logo - WITH BLACK TEXT */}
              <Link to="/" className="flex items-center space-x-3">
                <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2 rounded-xl">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <span className="font-display font-bold text-xl text-black">
                  MindCare AI
                </span>
              </Link>

              {/* Navigation Links */}
              <div className="flex space-x-1">
                <NavLink to="/" icon={UserPlus}>
                  Patient Intake
                </NavLink>
                <NavLink to="/admin" icon={LayoutDashboard}>
                  Admin Dashboard
                </NavLink>
                <NavLink to="/therapist" icon={Users}>
                  Therapist Portal
                </NavLink>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<PatientIntake />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/therapist" element={<TherapistDashboard />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white/50 border-t border-neutral-200 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="text-center text-sm text-neutral-600">
              <p className="font-medium">MindCare AI &copy; 2026</p>
              <p className="text-xs mt-1">Intelligent Mental Health Triage Platform</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

// Navigation Link Component
function NavLink({ to, icon: Icon, children }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium text-neutral-700 hover:bg-primary-50 hover:text-primary-700 transition-all duration-200 group"
    >
      <Icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
      <span>{children}</span>
    </Link>
  );
}

export default App;