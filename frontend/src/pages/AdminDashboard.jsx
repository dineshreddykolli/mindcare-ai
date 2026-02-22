/**
 * Admin Dashboard
 * Comprehensive overview of clinic operations, risk patients, and alerts
 */
import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Users, UserCheck, Clock, TrendingUp,
  Activity, Bell, CheckCircle, XCircle, AlertCircle
} from 'lucide-react';
import { adminAPI } from '../services/api';


// Utility: parse Postgres array string OR real JS array
const parseArray = (val) => {
  if (Array.isArray(val)) return val;
  if (typeof val === 'string') {
    return val.replace(/^{|}$/g, '').split(',').map(s => s.trim()).filter(Boolean);
  }
  return [];
};


function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [highRiskPatients, setHighRiskPatients] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [therapists, setTherapists] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [dashboardRes, patientsRes, alertsRes, therapistsRes] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getHighRiskPatients(10),
        adminAPI.getAlerts(null, 20),
        adminAPI.getTherapistCaseloads()
      ]);

      setDashboard(dashboardRes.data);
      setHighRiskPatients(patientsRes.data.patients);
      setAlerts(alertsRes.data.alerts);
      setTherapists(therapistsRes.data.therapists);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await adminAPI.acknowledgeAlert(alertId, 'admin@mindcare.com');
      loadDashboardData();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-neutral-900">
            Admin Dashboard
          </h1>
          <p className="text-neutral-600 mt-1">
            Real-time clinic operations and patient triage overview
          </p>
        </div>
        <button 
          onClick={loadDashboardData}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
        >
          <Activity className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Patients"
          value={dashboard?.overview?.active_patients || 0}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Intake Queue"
          value={dashboard?.overview?.intake_queue || 0}
          icon={Clock}
          color="yellow"
          subtitle="Waiting for assignment"
        />
        <MetricCard
          title="High Risk"
          value={dashboard?.overview?.high_risk_patients || 0}
          icon={AlertTriangle}
          color="red"
          subtitle={`${dashboard?.overview?.critical_patients || 0} critical`}
        />
        <MetricCard
          title="Active Alerts"
          value={dashboard?.overview?.active_alerts || 0}
          icon={Bell}
          color="purple"
          subtitle="Requires attention"
        />
      </div>

      {/* Therapist Utilization */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h2 className="text-xl font-display font-semibold text-neutral-900 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
          Therapist Utilization
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-neutral-50 rounded-lg p-4">
            <div className="text-sm text-neutral-600">Total Therapists</div>
            <div className="text-2xl font-bold text-neutral-900">
              {dashboard?.therapists?.total_active || 0}
            </div>
          </div>
          <div className="bg-neutral-50 rounded-lg p-4">
            <div className="text-sm text-neutral-600">Patients Assigned</div>
            <div className="text-2xl font-bold text-neutral-900">
              {dashboard?.therapists?.total_assigned_patients || 0}
            </div>
          </div>
          <div className="bg-neutral-50 rounded-lg p-4">
            <div className="text-sm text-neutral-600">Average Utilization</div>
            <div className="text-2xl font-bold text-primary-600">
              {dashboard?.therapists?.average_utilization_percent?.toFixed(1) || 0}%
            </div>
          </div>
        </div>

        {/* Therapist List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {therapists.slice(0, 5).map((therapist) => (
            <TherapistCard key={therapist.therapist_id} therapist={therapist} />
          ))}
        </div>
      </div>

      {/* High Risk Patients */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h2 className="text-xl font-display font-semibold text-neutral-900 mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2 text-danger-600" />
          High Risk Patients
        </h2>
        <div className="space-y-3">
          {highRiskPatients.length > 0 ? (
            highRiskPatients.map((patient) => (
              <PatientRiskCard key={patient.patient_id} patient={patient} />
            ))
          ) : (
            <div className="text-center py-8 text-neutral-500">
              No high-risk patients at this time
            </div>
          )}
        </div>
      </div>

      {/* Active Alerts */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h2 className="text-xl font-display font-semibold text-neutral-900 mb-4 flex items-center">
          <Bell className="w-5 h-5 mr-2 text-accent-600" />
          Active Alerts
        </h2>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {alerts.length > 0 ? (
            alerts.map((alert) => (
              <AlertCard 
                key={alert.alert_id} 
                alert={alert}
                onAcknowledge={handleAcknowledgeAlert}
              />
            ))
          ) : (
            <div className="text-center py-8 text-neutral-500">
              No active alerts
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


// Metric Card Component
function MetricCard({ title, value, icon: Icon, color, subtitle }) {
  const colorClasses = {
    blue: 'bg-primary-50 text-primary-600',
    yellow: 'bg-warning-50 text-warning-600',
    red: 'bg-danger-50 text-danger-600',
    purple: 'bg-accent-50 text-accent-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-card p-5 hover:shadow-soft transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600">{title}</p>
          <p className="text-3xl font-bold text-neutral-900 mt-2">{value}</p>
          {subtitle && (
            <p className="text-xs text-neutral-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}


// Therapist Card Component
function TherapistCard({ therapist }) {
  const utilizationColor = therapist.utilization_percent >= 90 
    ? 'bg-danger-500' 
    : therapist.utilization_percent >= 75 
    ? 'bg-warning-500' 
    : 'bg-success-500';

  return (
    <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors">
      <div className="flex-1">
        <div className="font-medium text-neutral-900">{therapist.name}</div>
        <div className="text-sm text-neutral-600">
          {parseArray(therapist.specialties).join(', ')}
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-right">
          <div className="text-sm font-medium text-neutral-900">
            {therapist.current_caseload}/{therapist.max_caseload}
          </div>
          <div className="text-xs text-neutral-500">patients</div>
        </div>
        <div className="w-24 bg-neutral-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${utilizationColor}`}
            style={{ width: `${therapist.utilization_percent}%` }}
          />
        </div>
      </div>
    </div>
  );
}


// Patient Risk Card Component
function PatientRiskCard({ patient }) {
  const riskColors = {
    critical: 'bg-danger-100 border-danger-300 text-danger-800',
    high: 'bg-warning-100 border-warning-300 text-warning-800',
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${riskColors[patient.risk_level]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="font-semibold">{patient.name}</div>
          <div className="text-sm mt-1 opacity-90">
            {patient.email} • {patient.phone}
          </div>
          {parseArray(patient.crisis_keywords).length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {parseArray(patient.crisis_keywords).map((keyword, i) => (
                <span key={i} className="px-2 py-1 bg-white/50 rounded text-xs font-medium">
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{patient.risk_score}</div>
          <div className="text-xs uppercase font-semibold">{patient.risk_level}</div>
          <div className="mt-2 px-3 py-1 bg-white rounded-full text-xs font-medium">
            {patient.urgency}
          </div>
        </div>
      </div>
    </div>
  );
}


// Alert Card Component
function AlertCard({ alert, onAcknowledge }) {
  const severityColors = {
    critical: 'border-danger-400 bg-danger-50',
    high: 'border-warning-400 bg-warning-50',
    medium: 'border-accent-400 bg-accent-50',
    low: 'border-primary-400 bg-primary-50',
  };

  return (
    <div className={`p-4 rounded-lg border-l-4 ${severityColors[alert.severity]}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-neutral-900">{alert.title}</span>
            <span className="px-2 py-0.5 bg-white rounded text-xs font-medium uppercase">
              {alert.severity}
            </span>
          </div>
          <div className="text-sm text-neutral-700 mt-1">{alert.description}</div>
          <div className="text-xs text-neutral-500 mt-2">
            {new Date(alert.created_at).toLocaleString()}
          </div>
        </div>
        {!alert.acknowledged && (
          <button
            onClick={() => onAcknowledge(alert.alert_id)}
            className="ml-4 px-3 py-1 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 transition-colors"
          >
            Acknowledge
          </button>
        )}
      </div>
    </div>
  );
}


export default AdminDashboard;
