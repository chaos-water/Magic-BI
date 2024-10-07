import { writable } from 'svelte/store';

export const selectedMode = writable('rag'); // 默认值
export const selectedConnector = writable('');
export const selectedDataset = writable('');
