// frontend/src/pages/Assistant.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatInterface from '../components/chat/ChatInterface';
import PatientHistory from '../components/chat/PatientHistory';
import ReportViewer from '../components/chat/ReportViewer';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import axios from 'axios';

const Assistant = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    fetchPatients();
  }, [isAuthenticated, navigate]);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/users/patients');
      setPatients(response.data);
    } catch (error) {
      console.error('Error fetching patients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
    setSelectedConversation(null);
  };

  const handleConversationSelect = (conversationId) => {
    setSelectedConversation(conversationId);
  };

  return (
    <div className="container mx-auto p-4 h-screen flex flex-col">
      <h1 className="text-2xl font-bold mb-4">Doctor Assistant</h1>
      
      <div className="grid grid-cols-12 gap-4 flex-1">
        {/* Patient List */}
        <div className="col-span-3">
          <Card className="h-full">
            <CardContent className="p-4">
              <h2 className="text-lg font-semibold mb-4">Patients</h2>
              {loading ? (
                <p>Loading patients...</p>
              ) : patients.length > 0 ? (
                <div className="space-y-2">
                  {patients.map((patient) => (
                    <Button
                      key={patient.id}
                      variant={selectedPatient?.id === patient.id ? "default" : "outline"}
                      className="w-full justify-start"
                      onClick={() => handlePatientSelect(patient)}
                    >
                      {patient.name}
                    </Button>
                  ))}
                </div>
              ) : (
                <p>No patients found</p>
              )}
            </CardContent>
          </Card>
        </div>
        
        {/* Patient History */}
        <div className="col-span-3">
          <PatientHistory 
            patientId={selectedPatient?.id} 
            onConversationSelect={handleConversationSelect}
            selectedConversationId={selectedConversation}
          />
        </div>
        
        {/* Chat Interface */}
        <div className="col-span-3">
          <ChatInterface patientId={selectedPatient?.id} />
        </div>
        
        {/* Report Viewer */}
        <div className="col-span-3">
          <ReportViewer 
            patientId={selectedPatient?.id}
            conversationId={selectedConversation}
          />
        </div>
      </div>
    </div>
  );
};

export default Assistant;