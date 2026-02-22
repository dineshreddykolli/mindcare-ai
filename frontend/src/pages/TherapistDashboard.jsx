/**
 * Therapist Dashboard
 * View caseload, patient assignments, and receive recommendations
 */
import React, { useState, useEffect } from 'react';
import { Users, Calendar, TrendingUp, AlertCircle } from 'lucide-react';
import { adminAPI } from '../services/api';


// Utility: parse Postgres array string OR real JS array
const parseArray = (val) => {
  if (Array.isArray(val)) return val;
  if (typeof val === 'string') {
    return val.replace(/^{|}$/g, '').split(',').map(s => s.trim()).filter(Boolean);
  }
  return [];
};


function TherapistDashboard() {
  const [therapists, setTherapists] = useState([]);
  const [selectedTherapist, setSelectedTherapist] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTherapistData();
  }, []);

  const loadTherapistData = async () => {
    try {
      const response = await adminAPI.getTherapistCaseloads();
      setTherapists(response.data.therapists);
      if (response.data.therapists.length > 0) {
        setSelectedTherapist(response.data.therapists[0]);
      }
    } catch (error) {
      console.error('Error loading therapist data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-neutral-900">
          Therapist Portal
        </h1>
        <p className="text-neutral-600 mt-1">
          View caseloads and manage patient assignments
        </p>
      </div>

      {/* Therapist Selector */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <label className="block text-sm font-medium text-neutral-700 mb-2">
          Select Therapist
        </label>
        <select
          value={selectedTherapist?.therapist_id || ''}
          onChange={(e) => {
            const therapist = therapists.find(t => t.therapist_id === e.target.value);
            setSelectedTherapist(therapist);
          }}
          className="w-full md:w-96 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {therapists.map((therapist) => (
            <option key={therapist.therapist_id} value={therapist.therapist_id}>
              {therapist.name}
            </option>
          ))}
        </select>
      </div>

      {selectedTherapist && (
        <>
          {/* Therapist Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              title="Current Caseload"
              value={`${selectedTherapist.current_caseload}/${selectedTherapist.max_caseload}`}
              icon={Users}
              color="blue"
            />
            <StatCard
              title="Utilization"
              value={`${selectedTherapist.utilization_percent}%`}
              icon={TrendingUp}
              color="green"
            />
            <StatCard
              title="Capacity Remaining"
              value={selectedTherapist.capacity_remaining}
              icon={Calendar}
              color="purple"
            />
            <StatCard
              title="High Risk Patients"
              value={selectedTherapist.accepts_high_risk ? 'Accepted' : 'Not Accepted'}
              icon={AlertCircle}
              color={selectedTherapist.accepts_high_risk ? 'green' : 'yellow'}
            />
          </div>

          {/* Therapist Details */}
          <div className="bg-white rounded-xl shadow-card p-6">
            <h2 className="text-xl font-display font-semibold text-neutral-900 mb-4">
              Therapist Profile
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-neutral-600 mb-2">Specialties</h3>
                <div className="flex flex-wrap gap-2">
                  {parseArray(selectedTherapist.specialties).map((specialty, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
                    >
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-neutral-600 mb-2">Languages</h3>
                <div className="flex flex-wrap gap-2">
                  {parseArray(selectedTherapist.languages).map((language, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm font-medium"
                    >
                      {language}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-neutral-600 mb-2">Experience</h3>
                <p className="text-neutral-900 font-semibold">
                  {selectedTherapist.years_experience} years
                </p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-neutral-600 mb-2">Contact</h3>
                <p className="text-neutral-900">{selectedTherapist.email}</p>
              </div>
            </div>
          </div>

          {/* Caseload Visualization */}
          <div className="bg-white rounded-xl shadow-card p-6">
            <h2 className="text-xl font-display font-semibold text-neutral-900 mb-4">
              Caseload Distribution
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-neutral-600">Active Patients</span>
                  <span className="font-semibold text-neutral-900">
                    {selectedTherapist.current_caseload}
                  </span>
                </div>
                <div className="w-full bg-neutral-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full ${
                      selectedTherapist.utilization_percent >= 90
                        ? 'bg-danger-500'
                        : selectedTherapist.utilization_percent >= 75
                        ? 'bg-warning-500'
                        : 'bg-success-500'
                    }`}
                    style={{ width: `${selectedTherapist.utilization_percent}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4">
                <div className="text-center p-4 bg-success-50 rounded-lg">
                  <div className="text-2xl font-bold text-success-700">
                    {selectedTherapist.utilization_percent < 75 ? '✓' : ''}
                  </div>
                  <div className="text-xs text-success-700 font-medium mt-1">
                    Good Capacity
                  </div>
                </div>
                <div className="text-center p-4 bg-warning-50 rounded-lg">
                  <div className="text-2xl font-bold text-warning-700">
                    {selectedTherapist.utilization_percent >= 75 && selectedTherapist.utilization_percent < 90 ? '!' : ''}
                  </div>
                  <div className="text-xs text-warning-700 font-medium mt-1">
                    Near Capacity
                  </div>
                </div>
                <div className="text-center p-4 bg-danger-50 rounded-lg">
                  <div className="text-2xl font-bold text-danger-700">
                    {selectedTherapist.utilization_percent >= 90 ? '⚠' : ''}
                  </div>
                  <div className="text-xs text-danger-700 font-medium mt-1">
                    At Capacity
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}


// Stat Card Component
function StatCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-primary-50 text-primary-600',
    green: 'bg-success-50 text-success-600',
    purple: 'bg-accent-50 text-accent-600',
    yellow: 'bg-warning-50 text-warning-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-card p-5 hover:shadow-soft transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600">{title}</p>
          <p className="text-2xl font-bold text-neutral-900 mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}


export default TherapistDashboard;
