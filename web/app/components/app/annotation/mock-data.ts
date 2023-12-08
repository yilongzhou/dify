import type { AnnotationItem, HitHistoryItem } from './type'

const list: AnnotationItem[] = [
  // create some mock data
  {
    id: '1',
    question: 'What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?',
    answer: 'What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?',
    created_at: '2020-01-01T00:00:00Z',
    hit_count: 1,
  },
  {
    id: '2',
    question: 'What is the capital of Canada?',
    answer: 'Ottawa',
    created_at: '2020-01-02T00:00:00Z',
    hit_count: 2,
  },
  {
    id: '3',
    question: 'What is the capital of Mexico?',
    answer: 'Mexico City',
    created_at: '2020-01-03T00:00:00Z',
    hit_count: 3,
  },
  {
    id: '4',
    question: 'What is the capital of Brazil?',
    answer: 'Brasilia',
    created_at: '2020-01-04T00:00:00Z',
    hit_count: 4,
  },
  {
    id: '5',
    question: 'What is the capital of Argentina?',
    answer: 'Buenos Aires',
    created_at: '2020-01-05T00:00:00Z',
    hit_count: 5,
  },
  {
    id: '6',
    question: 'What is the capital of Chile?',
    answer: 'Santiago',
    created_at: '2020-01-06T00:00:00Z',
    hit_count: 6,
  },
  {
    id: '7',
    question: 'What is the capital of Peru?',
    answer: 'Lima',
    created_at: '2020-01-07T00:00:00Z',
    hit_count: 7,
  },
  {
    id: '8',
    question: 'What is the capital of Ecuador?',
    answer: 'Quito',
    created_at: '2020-01-08T00:00:00Z',
    hit_count: 8,
  },
  {
    id: '9',
    question: 'What is the capital of Colombia?',
    answer: 'Bogota',
    created_at: '2020-01-09T00:00:00Z',
    hit_count: 9,
  },
]

export const hitHistoryList: HitHistoryItem[] = [
  // create some mock data. source can only be: API/Webapp/Explore/Debug
  {
    id: '1',
    question: 'What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?What is the capital of the United States?',
    source: 'API',
    score: 0.9,
    created_at: '2020-01-01T00:00:00Z',
  },
  {
    id: '2',
    question: 'What is the capital of Canada?',
    source: 'Webapp',
    score: 0.8,
    created_at: '2020-01-02T00:00:00Z',
  },
  {
    id: '3',
    question: 'What is the capital of Mexico?',
    source: 'Explore',
    score: 0.7,
    created_at: '2020-01-03T00:00:00Z',
  },
  {
    id: '4',
    question: 'What is the capital of Brazil?',
    source: 'Debug',
    score: 0.6,
    created_at: '2020-01-04T00:00:00Z',
  },
  {
    id: '5',
    question: 'What is the capital of Argentina?',
    source: 'API',
    score: 0.5,
    created_at: '2020-01-05T00:00:00Z',
  },
  {
    id: '6',
    question: 'What is the capital of Chile?',
    source: 'Webapp',
    score: 0.4,
    created_at: '2020-01-06T00:00:00Z',
  },
  {
    id: '7',
    question: 'What is the capital of Peru?',
    source: 'Explore',
    score: 0.3,
    created_at: '2020-01-07T00:00:00Z',
  },
  {
    id: '8',
    question: 'What is the capital of Ecuador?',
    source: 'Debug',
    score: 0.2,
    created_at: '2020-01-08T00:00:00Z',
  },
  {
    id: '9',
    question: 'What is the capital of Colombia?',
    source: 'API',
    score: 0.1,
    created_at: '2020-01-09T00:00:00Z',
  },
]

export default list
