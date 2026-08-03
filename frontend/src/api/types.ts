export interface AcceptanceCriteria {
  id: string;
  identifier: string;
  text: string;
  created_at: string;
}

export interface ExecutionLog {
  id: string;
  node: string;
  status: string;
  message: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface TestCase {
  id: string;
  qa_plan_id: string;
  title: string;
  description: string;
  test_type: string;
  category: string;
  acceptance_criteria_ids: string[];
  rationale: string;
  steps: string[];
  expected_result: string;
  preconditions?: string;
  status: string;
  priority: string;
  is_duplicate: boolean;
  is_incomplete: boolean;
  flag_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateTestCaseRequest {
  title?: string;
  description?: string;
  steps?: string[];
  expected_result?: string;
  rationale?: string;
  status?: string;
  priority?: string;
}

export interface QAPlanVersion {
  id: string;
  qa_plan_id: string;
  version_number: number;
  change_summary: string;
  snapshot: Record<string, any>;
  created_at: string;
}

export interface QAPlanResponse {
  id: string;
  title: string;
  status: string;
  current_version: number;
  created_at: string;
  updated_at: string;
}

export interface QAPlanDetailResponse extends QAPlanResponse {
  requirement_or_user_story: string;
  implementation_summary?: string;
  assumptions: string[];
  coverage_summary: Record<string, any>;
  acceptance_criteria: AcceptanceCriteria[];
  test_cases: TestCase[];
  versions: QAPlanVersion[];
  execution_logs: ExecutionLog[];
}

export interface GeneratePlanRequest {
  title: string;
  user_story: string;
  acceptance_criteria: string[];
  implementation_summary: string;
}

export interface CreateVersionRequest {
  change_summary: string;
}
