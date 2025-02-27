import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Star, AlertCircle, Info } from 'lucide-react';
import axios from 'axios';

const PatientHistory = ({ patientId }) => {
  const [loading, setLoading] = useState(true);
  const [patientData, setPatientData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [activeDocument, setActiveDocument] = useState(null);

  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        setLoading(true);
        // Fetch patient profile
        const profileResponse = await axios.get(`/api/patients/${patientId}`);
        setPatientData(profileResponse.data);
        
        // Fetch patient documents
        const documentsResponse = await axios.get(`/api/patients/${patientId}/documents`);
        setDocuments(documentsResponse.data);
        
        if (documentsResponse.data.length > 0) {
          setActiveDocument(documentsResponse.data[0]);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching patient data:', error);
        setLoading(false);
      }
    };

    if (patientId) {
      fetchPatientData();
    }
  }, [patientId]);

  const handleDocumentClick = (doc) => {
    setActiveDocument(doc);
  };

  const renderDocumentList = () => {
    return documents.map((doc) => (
      <div 
        key={doc._id} 
        className={`flex items-center p-3 border-b cursor-pointer hover:bg-gray-50 ${activeDocument?._id === doc._id ? 'bg-blue-50' : ''}`}
        onClick={() => handleDocumentClick(doc)}
      >
        <FileText className="mr-2 h-5 w-5 text-gray-500" />
        <div className="flex-1">
          <p className="text-sm font-medium">{doc.title}</p>
          <p className="text-xs text-gray-500">{new Date(doc.uploadDate).toLocaleDateString()}</p>
        </div>
        {doc.important && <AlertCircle className="h-4 w-4 text-red-500" />}
      </div>
    ));
  };

  const renderMedicalHistory = () => {
    if (!patientData?.medicalHistory) return <p>No medical history available.</p>;
    
    return (
      <div className="space-y-4">
        {patientData.medicalHistory.conditions.map((condition, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium">{condition.name}</h4>
                  <p className="text-sm text-gray-500">Diagnosed: {new Date(condition.diagnosedDate).toLocaleDateString()}</p>
                </div>
                {condition.active && (
                  <Badge variant="destructive">Active</Badge>
                )}
              </div>
              <p className="mt-2 text-sm">{condition.notes}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  const renderMedications = () => {
    if (!patientData?.medications || patientData.medications.length === 0) {
      return <p>No current medications.</p>;
    }
    
    return (
      <div className="space-y-3">
        {patientData.medications.map((med, index) => (
          <div key={index} className="p-3 border rounded-md">
            <div className="flex justify-between">
              <h4 className="font-medium">{med.name} ({med.dosage})</h4>
              {med.critical && (
                <Badge variant="destructive">Critical</Badge>
              )}
            </div>
            <p className="text-sm text-gray-500">Prescribed: {new Date(med.prescribedDate).toLocaleDateString()}</p>
            <p className="text-sm mt-1">Take {med.instructions}</p>
          </div>
        ))}
      </div>
    );
  };

  const renderDocumentContent = () => {
    if (!activeDocument) return <p>Select a document to view its content.</p>;
    
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">{activeDocument.title}</h3>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <FileText className="mr-2 h-4 w-4" />
              Download
            </Button>
            <Button variant="outline" size="sm">
              <Star className="mr-2 h-4 w-4" />
              Save to Quick Access
            </Button>
          </div>
        </div>
        
        <div className="border rounded-md p-4">
          <h4 className="font-medium mb-2">Extracted Information</h4>
          <div className="space-y-2">
            {activeDocument.extractedInfo?.map((info, index) => (
              <div key={index} className="flex items-start">
                <Info className="h-4 w-4 mr-2 mt-1 text-blue-500" />
                <div>
                  <span className="font-medium">{info.label}: </span>
                  <span>{info.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="border rounded-md p-4">
          <h4 className="font-medium mb-2">Document Content</h4>
          <div className="whitespace-pre-line text-sm">
            {activeDocument.content}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="text-center p-8">Loading patient data...</div>;
  }

  if (!patientData) {
    return <div className="text-center p-8">No patient data found.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle>Patient Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <h3 className="text-lg font-medium">{patientData.firstName} {patientData.lastName}</h3>
                <p className="text-sm text-gray-500">ID: {patientData.patientId}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-gray-500">Date of Birth</p>
                  <p>{new Date(patientData.dateOfBirth).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-gray-500">Gender</p>
                  <p>{patientData.gender}</p>
                </div>
                <div>
                  <p className="text-gray-500">Blood Type</p>
                  <p>{patientData.bloodType || 'Unknown'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Primary Doctor</p>
                  <p>{patientData.primaryDoctor}</p>
                </div>
              </div>
              
              <div>
                <p className="text-gray-500 text-sm">Contact Information</p>
                <p className="text-sm">{patientData.phoneNumber}</p>
                <p className="text-sm">{patientData.email}</p>
              </div>
              
              <div>
                <p className="text-gray-500 text-sm">Allergies</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {patientData.allergies && patientData.allergies.length > 0 ? (
                    patientData.allergies.map((allergy, index) => (
                      <Badge key={index} variant="outline" className="bg-red-50">
                        {allergy}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-sm">No known allergies</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Documents</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-96 overflow-y-auto">
              {documents.length > 0 ? (
                renderDocumentList()
              ) : (
                <p className="p-4 text-center text-gray-500">No documents available</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="md:col-span-2">
        <Tabs defaultValue="documents">
          <TabsList className="mb-4">
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="medical-history">Medical History</TabsTrigger>
            <TabsTrigger value="medications">Medications</TabsTrigger>
          </TabsList>
          
          <TabsContent value="documents">
            <Card>
              <CardContent className="p-4">
                {renderDocumentContent()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="medical-history">
            <Card>
              <CardHeader>
                <CardTitle>Medical History</CardTitle>
              </CardHeader>
              <CardContent>
                {renderMedicalHistory()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="medications">
            <Card>
              <CardHeader>
                <CardTitle>Current Medications</CardTitle>
              </CardHeader>
              <CardContent>
                {renderMedications()}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PatientHistory;