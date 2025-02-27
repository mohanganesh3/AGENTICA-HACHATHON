import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CheckCircle, AlertCircle, Info, Edit, Save, X } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';
import axios from 'axios';

const MetadataViewer = ({ document, onUpdate }) => {
  const [editMode, setEditMode] = useState(false);
  const [editedMetadata, setEditedMetadata] = useState({});
  const [loading, setLoading] = useState(false);

  const handleEditToggle = () => {
    if (editMode) {
      setEditMode(false);
    } else {
      setEditedMetadata(document.metadata || {});
      setEditMode(true);
    }
  };

  const handleMetadataChange = (key, value) => {
    setEditedMetadata({
      ...editedMetadata,
      [key]: value
    });
  };

  const handleSaveMetadata = async () => {
    try {
      setLoading(true);
      const response = await axios.put(`/api/documents/${document._id}/metadata`, {
        metadata: editedMetadata
      });
      
      if (response.status === 200) {
        onUpdate && onUpdate({
          ...document,
          metadata: editedMetadata
        });
        setEditMode(false);
      }
    } catch (error) {
      console.error('Error updating metadata:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderConfidenceIndicator = (confidence) => {
    if (confidence >= 0.9) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </TooltipTrigger>
            <TooltipContent>
              <p>High confidence ({Math.round(confidence * 100)}%)</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    } else if (confidence >= 0.7) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="h-4 w-4 text-blue-500" />
            </TooltipTrigger>
            <TooltipContent>
              <p>Medium confidence ({Math.round(confidence * 100)}%)</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    } else {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <AlertCircle className="h-4 w-4 text-amber-500" />
            </TooltipTrigger>
            <TooltipContent>
              <p>Low confidence ({Math.round(confidence * 100)}%)</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }
  };

  const renderMetadataTable = () => {
    if (!document.metadata || Object.keys(document.metadata).length === 0) {
      return <p className="text-gray-500 text-center p-4">No metadata available for this document.</p>;
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Field</TableHead>
            <TableHead>Value</TableHead>
            <TableHead className="w-20">Confidence</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Object.entries(document.metadata).map(([key, value]) => (
            <TableRow key={key}>
              <TableCell className="font-medium">{key}</TableCell>
              <TableCell>
                {editMode ? (
                  <Input 
                    value={editedMetadata[key] || ''} 
                    onChange={(e) => handleMetadataChange(key, e.target.value)}
                    className="h-8"
                  />
                ) : (
                  value.value
                )}
              </TableCell>
              <TableCell>
                {!editMode && renderConfidenceIndicator(value.confidence || 0)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  };

  const renderTagsSection = () => {
    if (!document.tags || document.tags.length === 0) {
      return <p className="text-gray-500 text-center p-4">No tags assigned to this document.</p>;
    }

    return (
      <div className="flex flex-wrap gap-2 p-2">
        {document.tags.map((tag, index) => (
          <Badge key={index} variant="secondary">
            {tag}
          </Badge>
        ))}
      </div>
    );
  };

  const renderComplianceSection = () => {
    if (!document.complianceChecks) {
      return <p className="text-gray-500 text-center p-4">No compliance information available.</p>;
    }

    return (
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <span className="font-medium">Overall Status:</span>
          {document.complianceChecks.compliant ? (
            <Badge variant="outline" className="bg-green-50 text-green-700">
              HIPAA Compliant
            </Badge>
          ) : (
            <Badge variant="outline" className="bg-red-50 text-red-700">
              Potential Compliance Issues
            </Badge>
          )}
        </div>

        {document.complianceChecks.issues && document.complianceChecks.issues.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium">Identified Issues:</h4>
            {document.complianceChecks.issues.map((issue, index) => (
              <div key={index} className="p-3 border-l-4 border-amber-500 bg-amber-50 rounded-r-md">
                <p className="font-medium">{issue.title}</p>
                <p className="text-sm">{issue.description}</p>
              </div>
            ))}
          </div>
        )}

        {document.complianceChecks.recommendations && (
          <div className="space-y-2">
            <h4 className="font-medium">Recommendations:</h4>
            <p className="text-sm">{document.complianceChecks.recommendations}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Document Metadata</CardTitle>
        <Button variant="outline" size="sm" onClick={handleEditToggle}>
          {editMode ? (
            <>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </>
          ) : (
            <>
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </>
          )}
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="metadata">
          <TabsList className="mb-4">
            <TabsTrigger value="metadata">Extracted Data</TabsTrigger>
            <TabsTrigger value="tags">Tags</TabsTrigger>
            <TabsTrigger value="compliance">Compliance</TabsTrigger>
          </TabsList>
          
          <TabsContent value="metadata">
            {renderMetadataTable()}
            
            {editMode && (
              <div className="mt-4 flex justify-end">
                <Button 
                  onClick={handleSaveMetadata} 
                  disabled={loading}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="tags">
            {renderTagsSection()}
          </TabsContent>
          
          <TabsContent value="compliance">
            {renderComplianceSection()}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default MetadataViewer;