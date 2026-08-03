import React, { useState } from 'react';
import { Check, X, Edit2, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import type { TestCase } from '../api/types';
import { QAPlanService } from '../api/services';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Textarea } from './ui/Textarea';

interface TestCaseEditorProps {
  testCase: TestCase;
  onUpdate: (updated: TestCase) => void;
}

export const TestCaseEditor: React.FC<TestCaseEditorProps> = ({ testCase, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    title: testCase.title,
    description: testCase.description,
    rationale: testCase.rationale,
    expected_result: testCase.expected_result,
    priority: testCase.priority,
  });

  const handleStatusChange = async (status: string) => {
    try {
      setLoadingAction(status);
      const updated = await QAPlanService.updateTestCase(testCase.id, { status });
      onUpdate(updated);
      toast.success(`Test case marked as ${status}`);
    } catch (err) {
      toast.error('Failed to update status');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleSaveEdit = async () => {
    try {
      setLoadingAction('EDIT');
      const updated = await QAPlanService.updateTestCase(testCase.id, {
        ...editForm,
        status: 'EDITED'
      });
      onUpdate(updated);
      setIsEditing(false);
      toast.success('Test case updated successfully');
    } catch (err) {
      toast.error('Failed to save edits');
    } finally {
      setLoadingAction(null);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  if (isEditing) {
    return (
      <Card className="border-indigo-500/50 shadow-lg shadow-indigo-500/10">
        <div className="space-y-4">
          <Input 
            label="Title" 
            value={editForm.title} 
            onChange={e => setEditForm({...editForm, title: e.target.value})} 
          />
          <div className="grid grid-cols-2 gap-4">
            <Input 
              label="Priority" 
              value={editForm.priority} 
              onChange={e => setEditForm({...editForm, priority: e.target.value})} 
            />
          </div>
          <Textarea 
            label="Description" 
            value={editForm.description} 
            onChange={e => setEditForm({...editForm, description: e.target.value})} 
            rows={2}
          />
          <Textarea 
            label="Rationale" 
            value={editForm.rationale} 
            onChange={e => setEditForm({...editForm, rationale: e.target.value})} 
            rows={2}
          />
          <Textarea 
            label="Expected Result" 
            value={editForm.expected_result} 
            onChange={e => setEditForm({...editForm, expected_result: e.target.value})} 
            rows={2}
          />
          
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={() => setIsEditing(false)} disabled={loadingAction !== null}>Cancel</Button>
            <Button onClick={handleSaveEdit} isLoading={loadingAction === 'EDIT'}>Save Changes</Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`transition-all ${testCase.status === 'REJECTED' ? 'opacity-60' : ''}`}>
      <div className="flex justify-between items-start gap-4 mb-3">
        <div>
          <div className="flex flex-wrap gap-2 mb-2">
            <Badge variant="purple">{testCase.test_type}</Badge>
            <Badge variant="default">{testCase.category}</Badge>
            <Badge variant={getPriorityColor(testCase.priority)}>{testCase.priority}</Badge>
            {testCase.status !== 'PROPOSED' && (
              <Badge variant={testCase.status === 'APPROVED' ? 'success' : testCase.status === 'REJECTED' ? 'error' : 'info'}>
                {testCase.status}
              </Badge>
            )}
          </div>
          <h4 className="text-lg font-semibold text-slate-200">{testCase.title}</h4>
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={() => setIsEditing(true)} title="Edit" disabled={loadingAction !== null}>
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button 
            size="sm" 
            variant="ghost" 
            className={`text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 ${testCase.status.toUpperCase() === 'APPROVED' ? 'opacity-30 cursor-not-allowed text-emerald-900/50' : ''}`}
            onClick={() => handleStatusChange('APPROVED')} 
            isLoading={loadingAction === 'APPROVED'} 
            disabled={loadingAction !== null || testCase.status.toUpperCase() === 'APPROVED'}
            title="Approve"
          >
            {loadingAction !== 'APPROVED' && <Check className="h-4 w-4" />}
          </Button>
          <Button 
            size="sm" 
            variant="ghost" 
            className={`text-red-400 hover:text-red-300 hover:bg-red-500/10 ${testCase.status.toUpperCase() === 'REJECTED' ? 'opacity-30 cursor-not-allowed text-red-900/50' : ''}`}
            onClick={() => handleStatusChange('REJECTED')} 
            isLoading={loadingAction === 'REJECTED'} 
            disabled={loadingAction !== null || testCase.status.toUpperCase() === 'REJECTED'}
            title="Reject"
          >
            {loadingAction !== 'REJECTED' && <X className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      <p className="text-slate-400 text-sm mb-4">{testCase.description}</p>
      
      {testCase.is_duplicate || testCase.is_incomplete ? (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 mb-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
          <div className="text-sm text-amber-200/80">
            <span className="font-semibold text-amber-400">Flagged by AI: </span>
            {testCase.flag_reason || 'Needs review.'}
          </div>
        </div>
      ) : null}

      <div className="space-y-4 text-sm bg-slate-900/50 p-4 rounded-lg border border-slate-800/50">
        <div>
          <span className="font-semibold text-slate-300">Rationale: </span>
          <span className="text-slate-400">{testCase.rationale}</span>
        </div>
        <div>
          <span className="font-semibold text-slate-300 block mb-1">Steps:</span>
          <ol className="list-decimal list-inside text-slate-400 space-y-1 ml-1">
            {testCase.steps.map((step, i) => <li key={i}>{step}</li>)}
          </ol>
        </div>
        <div>
          <span className="font-semibold text-slate-300">Expected Result: </span>
          <span className="text-slate-400">{testCase.expected_result}</span>
        </div>
        {testCase.acceptance_criteria_ids.length > 0 && (
          <div className="pt-2">
            <span className="font-semibold text-slate-300 mr-2">Covers:</span>
            {testCase.acceptance_criteria_ids.map(id => (
              <Badge key={id} variant="default" className="mr-1">{id}</Badge>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};
