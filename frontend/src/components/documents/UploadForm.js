// frontend/src/components/documents/UploadForm.js
import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { Loader2 } from 'lucide-react';

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [patientId, setPatientId] = useState('');
  const [patientName, setPatientName] = useState('');
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !patientId || !patientName) {
      toast({
        variant: "destructive",
        title: "Missing Information",
        description: "Please fill in all required fields.",
      });
      return;
    }
    
    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id', patientId);
    formData.append('patient_name', patientName);
    formData.append('notes', notes);
    
    try {
      // Upload the document
      const response = await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      
      const { document_id } = response.data;
      
      // Show success message
      toast({
        title: "Document Uploaded",
        description: "Your document is being processed. This may take a few moments.",
      });
      
      // Poll for processing completion
      const processingInterval = setInterval(async () => {
        try {
          const processingResponse = await axios.get(`/api/documents/${document_id}`);
          if (processingResponse.data.processed) {
            clearInterval(processingInterval);
            toast({
              title: "Processing Complete",
              description: `Document classified as: ${processingResponse.data.metadata.document_type}`,
            });
            // Reset form
            setFile(null);
            setPatientId('');
            setPatientName('');
            setNotes('');
            setUploading(false);
            setProgress(0);
          }
        } catch (error) {
          console.error("Error checking processing status:", error);
        }
      }, 5000); // Check every 5 seconds
      
    } catch (error) {
      console.error("Error uploading document:", error);
      toast({
        variant: "destructive",
        title: "Upload Failed",
        description: error.response?.data?.message || "An error occurred during upload.",
      });
      setUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Medical Document</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="file">Select Document</Label>
            <Input 
              id="file" 
              type="file" 
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" 
              onChange={handleFileChange}
              disabled={uploading}
            />
            {file && (
              <p className="text-sm text-gray-500">{file.name} ({Math.round(file.size / 1024)} KB)</p>
            )}
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="patientId">Patient ID</Label>
            <Input 
              id="patientId" 
              value={patientId} 
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="Enter patient ID"
              disabled={uploading}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="patientName">Patient Name</Label>
            <Input 
              id="patientName" 
              value={patientName} 
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient full name"
              disabled={uploading}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea 
              id="notes" 
              value={notes} 
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Enter any additional notes about this document"
              disabled={uploading}
              rows={3}
            />
          </div>
          
          {uploading && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${progress}%` }}
              ></div>
              <p className="text-sm text-center mt-1">Processing document... {progress}%</p>
            </div>
          )}
          
          <Button 
            type="submit"
            className="w-full"
            disabled={uploading || !file || !patientId || !patientName}
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : "Upload Document"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}