import { apiClient } from './client';
import type {
  QAPlanResponse,
  QAPlanDetailResponse,
  GeneratePlanRequest,
  TestCase,
  UpdateTestCaseRequest,
  QAPlanVersion,
  CreateVersionRequest,
} from './types';

export const QAPlanService = {
  // Plans
  listPlans: async (): Promise<QAPlanResponse[]> => {
    const { data } = await apiClient.get<QAPlanResponse[]>('/plans');
    return data;
  },
  
  getPlan: async (id: string): Promise<QAPlanDetailResponse> => {
    const { data } = await apiClient.get<QAPlanDetailResponse>(`/plans/${id}`);
    return data;
  },

  createPlan: async (payload: GeneratePlanRequest): Promise<QAPlanResponse> => {
    const { data } = await apiClient.post<QAPlanResponse>('/plans', payload);
    return data;
  },

  updatePlan: async (id: string, payload: { status: string }): Promise<QAPlanResponse> => {
    const { data } = await apiClient.patch<QAPlanResponse>(`/plans/${id}`, payload);
    return data;
  },

  deletePlan: async (id: string): Promise<void> => {
    await apiClient.delete(`/plans/${id}`);
  },

  // Test Cases
  updateTestCase: async (id: string, payload: UpdateTestCaseRequest): Promise<TestCase> => {
    const { data } = await apiClient.patch<TestCase>(`/test-cases/${id}`, payload);
    return data;
  },

  // Versions
  listVersions: async (planId: string): Promise<QAPlanVersion[]> => {
    const { data } = await apiClient.get<QAPlanVersion[]>(`/plans/${planId}/versions`);
    return data;
  },

  createVersion: async (planId: string, payload: CreateVersionRequest): Promise<QAPlanVersion> => {
    const { data } = await apiClient.post<QAPlanVersion>(`/plans/${planId}/versions`, payload);
    return data;
  },

  getVersion: async (planId: string, versionNumber: number): Promise<QAPlanVersion> => {
    const { data } = await apiClient.get<QAPlanVersion>(`/plans/${planId}/versions/${versionNumber}`);
    return data;
  }
};
