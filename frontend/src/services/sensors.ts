import { api, USE_MOCK } from './api';
import { mock } from './mock';
import { Sensor, SensorWithSecret } from '@/types';

export async function listSensors(): Promise<Sensor[]> {
  if (USE_MOCK) return mock.listSensors();
  const res = await api.get<Sensor[]>('/sensors');
  return res.data;
}

export async function createSensor(name: string, location: string): Promise<SensorWithSecret> {
  if (USE_MOCK) return mock.createSensor(name, location);
  const res = await api.post<SensorWithSecret>('/sensors', { name, location });
  return res.data;
}

export async function deleteSensor(id: number): Promise<void> {
  if (USE_MOCK) return mock.deleteSensor(id);
  await api.delete(`/sensors/${id}`);
}
