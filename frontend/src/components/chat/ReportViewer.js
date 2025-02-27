// frontend/src/components/chat/ReportViewer.js
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Printer, Download, Share2 } from 'lucide-react';
import axios from 'axios';

const ReportViewer = ({ patientId, conversationId }) => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    if (patientId && conversationId) {
      fetchReport();
    }
  }, [patientId, conversationId]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/chat/report/${conversationId}`);
      setReport(response.data);
    } catch (error) {
      console.error('Error fetching report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/chat/report/generate', {
        patientId,
        conversationId,
      });
      setReport(response.data);
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    // Implementation for downloading the report
    const element = document.createElement('a');
    const file = new Blob([JSON.stringify(report)], { type: 'application/json' });
    element.href = URL.createObjectURL(file);
    element.download = `patient-report-${patientId}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handlePrint = () => {
    window.print();
  };

  if (!patientId || !conversationId) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Report Viewer</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">
            Select a patient and conversation to view or generate a report
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Medical Report</CardTitle>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrint}
            disabled={!report}
          >
            <Printer className="h-4 w-4 mr-2" />
            Print
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
            disabled={!report}
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!report}
          >
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <p>Loading report...</p>
          </div>
        ) : report ? (
          <div className="space-y-4">
            <Tabs defaultValue="summary" onValueChange={setActiveTab} value={activeTab}>
              <TabsList className="grid grid-cols-4 mb-4">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="assessment">Assessment</TabsTrigger>
                <TabsTrigger value="plan">Plan</TabsTrigger>
                <TabsTrigger value="notes">Notes</TabsTrigger>
              </TabsList>
              
              <TabsContent value="summary" className="space-y-4">
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Patient Information</h3>
                  <p>Name: {report.patientName}</p>
                  <p>ID: {report.patientId}</p>
                  <p>Date: {new Date(report.timestamp).toLocaleDateString()}</p>
                </div>
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Consultation Summary</h3>
                  <p>{report.summary}</p>
                </div>
              </TabsContent>
              
              <TabsContent value="assessment" className="space-y-4">
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Clinical Assessment</h3>
                  <p>{report.assessment}</p>
                </div>
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Findings</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {report.findings.map((finding, index) => (
                      <li key={index}>{finding}</li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
              
              <TabsContent value="plan" className="space-y-4">
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Treatment Plan</h3>
                  <p>{report.plan}</p>
                </div>
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Recommendations</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {report.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
              
              <TabsContent value="notes" className="space-y-4">
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Doctor's Notes</h3>
                  <p>{report.notes}</p>
                </div>
                <div className="border p-4 rounded-md">
                  <h3 className="font-medium mb-2">Follow-up</h3>
                  <p>{report.followUp}</p>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 h-64">
            <p className="text-muted-foreground">No report available for this conversation</p>
            <Button onClick={handleGenerateReport}>
              Generate Report
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ReportViewer;