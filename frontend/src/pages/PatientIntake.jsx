/**
 * Patient Intake Page
 * AI-powered chatbot intake and comprehensive questionnaire
 */
import React, { useState } from 'react';
import { Send, MessageCircle, FileText, CheckCircle2, Loader } from 'lucide-react';
import { intakeAPI } from '../services/api';


function PatientIntake() {
  const [step, setStep] = useState(1);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m here to help you get started with MindCare. Can you tell me what brings you here today?' }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    patient_info: {},
    phq9_responses: {},
    gad7_responses: {},
    text_responses: {},
    preferences: {},
  });
  const [submissionResult, setSubmissionResult] = useState(null);


  const handleChatSend = async () => {
    if (!currentMessage.trim()) return;

    const userMessage = { role: 'user', content: currentMessage };
    const updatedMessages = [...chatMessages, userMessage];
    setChatMessages(updatedMessages);
    setCurrentMessage('');
    setLoading(true);

    try {
      const response = await intakeAPI.chatMessage(
        currentMessage,
        updatedMessages
      );
      setChatMessages([
        ...updatedMessages,
        { role: 'assistant', content: response.data.bot_message }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages([
        ...updatedMessages,
        { role: 'assistant', content: 'I apologize, but I encountered an error. Please try again.' }
      ]);
    } finally {
      setLoading(false);
    }
  };


  const handleFormUpdate = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };


  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.patient_info.first_name || !formData.patient_info.last_name || !formData.patient_info.email) {
      alert('Please fill in your name and email in the Basic Information section.');
      return;
    }

    if (!formData.patient_info.date_of_birth) {
      alert('Please enter your date of birth.');
      return;
    }

    if (!formData.text_responses.primary_concern || formData.text_responses.primary_concern.trim() === '') {
      alert('Please describe your primary concern before submitting.');
      return;
    }

    console.log('Submitting form data:', formData);

    setLoading(true);
    try {
      const response = await intakeAPI.submitIntake({
        ...formData,
        chatbot_transcript: chatMessages
      });
      setSubmissionResult(response.data);
      setStep(4);
    } catch (error) {
      console.error('Submission error:', error);
      const errorMsg = error.response?.data?.detail || 'Error submitting intake. Please try again.';
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <StepIndicator number={1} active={step >= 1} completed={step > 1} label="Introduction" />
          <div className="flex-1 h-1 bg-neutral-200 mx-2">
            <div className={`h-full transition-all ${step > 1 ? 'bg-primary-600' : 'bg-neutral-200'}`} />
          </div>
          <StepIndicator number={2} active={step >= 2} completed={step > 2} label="Initial Chat" />
          <div className="flex-1 h-1 bg-neutral-200 mx-2">
            <div className={`h-full transition-all ${step > 2 ? 'bg-primary-600' : 'bg-neutral-200'}`} />
          </div>
          <StepIndicator number={3} active={step >= 3} completed={step > 3} label="Questionnaire" />
          <div className="flex-1 h-1 bg-neutral-200 mx-2">
            <div className={`h-full transition-all ${step > 3 ? 'bg-primary-600' : 'bg-neutral-200'}`} />
          </div>
          <StepIndicator number={4} active={step >= 4} completed={step > 4} label="Complete" />
        </div>
      </div>


      {/* Step 1: Introduction */}
      {step === 1 && (
        <div className="animate-fade-in space-y-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-6 shadow-lg">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-4xl font-display font-bold text-neutral-900 mb-4">
              Welcome to MindCare AI
            </h1>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              We're here to help you get the right care, quickly. Our AI-assisted intake process will
              help us understand your needs and match you with the best therapist.
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-soft p-6 sm:p-8 max-w-3xl mx-auto">
            <h2 className="text-2xl font-semibold text-neutral-900 mb-6">
              What to expect:
            </h2>
            <div className="space-y-4 mb-8">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-neutral-900 mb-1">Brief chat about your concerns (5 minutes)</h3>
                  <p className="text-sm text-neutral-600">Have a conversation with our AI assistant about what brings you here</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-accent-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-neutral-900 mb-1">Standard mental health questionnaires (10 minutes)</h3>
                  <p className="text-sm text-neutral-600">Complete validated assessments to help us understand your symptoms</p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-neutral-900 mb-1">AI-powered therapist matching based on your needs</h3>
                  <p className="text-sm text-neutral-600">Get matched with the best therapist for your specific situation</p>
                </div>
              </div>
            </div>

            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <div className="text-sm text-primary-900 flex-1">
                  <p className="font-medium mb-1">Your privacy is protected</p>
                  <p className="text-primary-800">All information is confidential and HIPAA-compliant. This assessment typically takes 15-20 minutes.</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
            >
              Get Started
              <svg className="inline-block ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
          </div>
        </div>
      )}


      {/* Step 2: Chatbot */}
      {step === 2 && (
        <div className="bg-white rounded-2xl shadow-soft overflow-hidden animate-fade-in">
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white">
            <h2 className="text-2xl font-display font-bold">Let's Talk</h2>
            <p className="text-primary-100 mt-1">Share your concerns in your own words</p>
          </div>

          <div className="h-96 overflow-y-auto p-6 space-y-4 bg-neutral-50">
            {chatMessages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}
            {loading && (
              <div className="flex items-center space-x-2 text-neutral-500">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is typing...</span>
              </div>
            )}
          </div>

          <div className="p-4 bg-white border-t border-neutral-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={loading}
              />
              <button
                onClick={handleChatSend}
                disabled={loading || !currentMessage.trim()}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <button
              onClick={() => setStep(3)}
              className="mt-4 w-full px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors font-medium"
            >
              Continue to Questionnaire →
            </button>
          </div>
        </div>
      )}


      {/* Step 3: Questionnaire */}
      {step === 3 && (
        <div className="space-y-6 animate-fade-in">
          <IntakeQuestionnaire formData={formData} onUpdate={handleFormUpdate} />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium text-lg disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <FileText className="w-5 h-5" />
                <span>Submit Intake</span>
              </>
            )}
          </button>
        </div>
      )}


      {/* Step 4: Complete */}
      {step === 4 && submissionResult && (
        <div className="bg-white rounded-2xl shadow-soft p-8 text-center animate-fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mb-4">
            <CheckCircle2 className="w-8 h-8 text-success-600" />
          </div>
          <h2 className="text-3xl font-display font-bold text-neutral-900 mb-4">
            Intake Complete!
          </h2>
          <p className="text-lg text-neutral-600 mb-6">
            Thank you for completing your intake. We've assessed your needs.
          </p>

          <div className="bg-neutral-50 rounded-lg p-6 mb-6 max-w-md mx-auto">
            <div className="text-sm text-neutral-600 mb-2">Your Risk Assessment</div>
            <div className={`text-4xl font-bold mb-2 ${
              submissionResult.risk_assessment.risk_level === 'critical' ? 'text-danger-600' :
              submissionResult.risk_assessment.risk_level === 'high' ? 'text-warning-600' :
              'text-success-600'
            }`}>
              {submissionResult.risk_assessment.risk_level.toUpperCase()}
            </div>
            <div className="text-sm text-neutral-600">
              Priority: {submissionResult.risk_assessment.urgency}
            </div>
          </div>

          <p className="text-neutral-700 mb-6">
            {submissionResult.message}
          </p>

          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Start New Intake
          </button>
        </div>
      )}
    </div>
  );
}


// Step Indicator Component
function StepIndicator({ number, active, completed, label }) {
  return (
    <div className="flex flex-col items-center">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
        completed ? 'bg-primary-600 text-white' :
        active ? 'bg-primary-100 text-primary-700 ring-2 ring-primary-600' :
        'bg-neutral-200 text-neutral-500'
      }`}>
        {completed ? <CheckCircle2 className="w-5 h-5" /> : number}
      </div>
      <div className={`text-xs mt-2 font-medium ${active ? 'text-primary-700' : 'text-neutral-500'}`}>
        {label}
      </div>
    </div>
  );
}


// Chat Message Component
function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
        isUser
          ? 'bg-primary-600 text-white'
          : 'bg-white text-neutral-900 shadow-sm border border-neutral-200'
      }`}>
        <p className="text-sm leading-relaxed">{message.content}</p>
      </div>
    </div>
  );
}


// Intake Questionnaire Component
function IntakeQuestionnaire({ formData, onUpdate }) {
  const phq9Questions = [
    { id: 'interest', text: 'Little interest or pleasure in doing things' },
    { id: 'depressed', text: 'Feeling down, depressed, or hopeless' },
    { id: 'sleep', text: 'Trouble falling/staying asleep or sleeping too much' },
    { id: 'fatigue', text: 'Feeling tired or having little energy' },
    { id: 'appetite', text: 'Poor appetite or overeating' },
    { id: 'failure', text: 'Feeling bad about yourself or that you are a failure' },
    { id: 'concentration', text: 'Trouble concentrating on things' },
    { id: 'movement', text: 'Moving or speaking slowly or being fidgety/restless' },
    { id: 'self_harm', text: 'Thoughts that you would be better off dead or hurting yourself' },
  ];

  const responseOptions = [
    { value: 0, label: 'Not at all' },
    { value: 1, label: 'Several days' },
    { value: 2, label: 'More than half the days' },
    { value: 3, label: 'Nearly every day' },
  ];

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h3 className="text-xl font-display font-semibold text-neutral-900 mb-4">
          Basic Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              First Name <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              placeholder="First Name"
              required
              onChange={(e) => onUpdate('patient_info', 'first_name', e.target.value)}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Last Name <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              placeholder="Last Name"
              required
              onChange={(e) => onUpdate('patient_info', 'last_name', e.target.value)}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Email <span className="text-red-600">*</span>
            </label>
            <input
              type="email"
              placeholder="Email"
              required
              onChange={(e) => onUpdate('patient_info', 'email', e.target.value)}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Phone
            </label>
            <input
              type="tel"
              placeholder="Phone"
              onChange={(e) => onUpdate('patient_info', 'phone', e.target.value)}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="col-span-1 md:col-span-2">
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Date of Birth <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              required
              onChange={(e) => onUpdate('patient_info', 'date_of_birth', e.target.value)}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* PHQ-9 Depression Screening */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h3 className="text-xl font-display font-semibold text-neutral-900 mb-2">
          Depression Screening (PHQ-9)
        </h3>
        <p className="text-sm text-neutral-600 mb-4">
          Over the last 2 weeks, how often have you been bothered by the following problems?
        </p>
        <div className="space-y-4">
          {phq9Questions.map((q) => (
            <QuestionRow
              key={q.id}
              question={q.text}
              options={responseOptions}
              onChange={(value) => onUpdate('phq9_responses', q.id, value)}
            />
          ))}
        </div>
      </div>

      {/* GAD-7 Anxiety Screening */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h3 className="text-xl font-display font-semibold text-neutral-900 mb-2">
          Anxiety Screening (GAD-7)
        </h3>
        <p className="text-sm text-neutral-600 mb-4">
          Over the last 2 weeks, how often have you been bothered by the following problems?
        </p>
        <div className="space-y-4">
          <QuestionRow
            question="Feeling nervous, anxious, or on edge"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'nervous', value)}
          />
          <QuestionRow
            question="Not being able to stop or control worrying"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'control_worry', value)}
          />
          <QuestionRow
            question="Worrying too much about different things"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'worry_much', value)}
          />
          <QuestionRow
            question="Trouble relaxing"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'trouble_relaxing', value)}
          />
          <QuestionRow
            question="Being so restless that it's hard to sit still"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'restless', value)}
          />
          <QuestionRow
            question="Becoming easily annoyed or irritable"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'irritable', value)}
          />
          <QuestionRow
            question="Feeling afraid as if something awful might happen"
            options={responseOptions}
            onChange={(value) => onUpdate('gad7_responses', 'afraid', value)}
          />
        </div>
      </div>

      {/* Text Responses */}
      <div className="bg-white rounded-xl shadow-card p-6">
        <h3 className="text-xl font-display font-semibold text-neutral-900 mb-4">
          Tell Us More
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              What is your primary concern? <span className="text-red-600">*</span>
            </label>
            <textarea
              placeholder="What is your primary concern or reason for seeking therapy?"
              required
              onChange={(e) => onUpdate('text_responses', 'primary_concern', e.target.value)}
              className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 h-24 resize-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Describe your symptoms (optional)
            </label>
            <textarea
              placeholder="Describe any symptoms you've been experiencing..."
              onChange={(e) => onUpdate('text_responses', 'symptoms_description', e.target.value)}
              className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 h-24 resize-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              What are your goals for therapy? (optional)
            </label>
            <textarea
              placeholder="What are your goals for therapy?"
              onChange={(e) => onUpdate('text_responses', 'goals_for_therapy', e.target.value)}
              className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 h-24 resize-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
}


// Question Row Component
function QuestionRow({ question, options, onChange }) {
  const [selected, setSelected] = useState(null);

  const handleSelect = (value) => {
    setSelected(value);
    onChange(value);
  };

  return (
    <div className="border-b border-neutral-200 pb-4 last:border-0">
      <p className="text-sm text-neutral-700 mb-3">{question}</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => handleSelect(opt.value)}
            className={`px-3 py-2 border rounded-lg transition-all text-xs font-medium ${
              selected === opt.value
                ? 'border-primary-600 bg-primary-50 text-primary-700'
                : 'border-neutral-300 hover:border-primary-400 hover:bg-primary-50'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}


export default PatientIntake;
