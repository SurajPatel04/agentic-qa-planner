import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, History } from 'lucide-react';
import { toast } from 'react-toastify';
import { QAPlanService } from '../api/services';
import type { QAPlanVersion } from '../api/types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const VersionSnapshot: React.FC = () => {
  const { id, version } = useParams<{ id: string; version: string }>();
  const navigate = useNavigate();
  const [snapshot, setSnapshot] = useState<QAPlanVersion | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVersion = async () => {
      if (!id || !version) return;
      try {
        setLoading(true);
        const data = await QAPlanService.getVersion(id, parseInt(version));
        setSnapshot(data);
      } catch (err) {
        toast.error('Failed to load version snapshot');
        navigate(`/plans/${id}`);
      } finally {
        setLoading(false);
      }
    };
    fetchVersion();
  }, [id, version, navigate]);

  if (loading || !snapshot) {
    return (
      <div className="flex justify-center items-center h-full pt-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  const data = snapshot.snapshot;

  return (
    <div className="max-w-5xl mx-auto pb-20 space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/plans/${id}`)} leftIcon={<ArrowLeft className="h-4 w-4" />}>
        Back to current plan
      </Button>

      <div className="flex items-center gap-3">
        <Badge variant="purple" className="text-lg px-3 py-1">v{snapshot.version_number}</Badge>
        <h1 className="text-3xl font-bold text-slate-100 flex items-center gap-2">
          <History className="h-7 w-7 text-indigo-400" />
          {snapshot.change_summary}
        </h1>
      </div>
      <p className="text-slate-400">Captured {new Date(snapshot.created_at).toLocaleString()}</p>

      <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 text-amber-200/80 text-sm">
        <span className="font-semibold text-amber-400">Read Only: </span>
        This is a historical snapshot. It cannot be edited.
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-xl font-semibold mb-4 text-slate-200">Requirements State</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-slate-300 mb-1">User Story</h3>
              <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50 text-sm text-slate-400 whitespace-pre-wrap">
                {data.user_story}
              </div>
            </div>
            {data.implementation_summary && (
              <div>
                <h3 className="font-medium text-slate-300 mb-1">Implementation Summary</h3>
                <div className="bg-slate-900/50 p-3 rounded border border-slate-800/50 text-sm text-slate-400 whitespace-pre-wrap">
                  {data.implementation_summary}
                </div>
              </div>
            )}
            <div>
              <h3 className="font-medium text-slate-300 mb-1">Acceptance Criteria</h3>
              <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
                {data.acceptance_criteria.map((ac: string, i: number) => <li key={i}>{ac}</li>)}
              </ul>
            </div>
          </div>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold mb-4 text-slate-200">Generated Tests ({data.test_cases.length})</h2>
          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
            {data.test_cases.map((tc: any, i: number) => (
              <div key={i} className="bg-slate-900/50 p-4 rounded-lg border border-slate-800/50">
                <div className="flex gap-2 mb-2">
                  <Badge variant="purple">{tc.test_type}</Badge>
                  <Badge>{tc.status}</Badge>
                </div>
                <h4 className="font-semibold text-slate-200 mb-1">{tc.title}</h4>
                <p className="text-sm text-slate-400 line-clamp-2">{tc.description}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
