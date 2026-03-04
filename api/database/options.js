import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const dataDir = path.join(process.cwd(), 'public', 'data');
    const dataFile = path.join(dataDir, 'database.json');
    
    if (!fs.existsSync(dataFile)) {
      return res.json({ 
        options: {
          链路: ['低价', '中价', '正价'],
          学段: ['小学', '初中', '高中', '低幼'],
          竞品: ['作业帮', '猿辅导', '高途', '希望学', '豆神', '叫叫', 'IP'],
          学科: ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '多科']
        },
        total: 0,
        message: 'No data file found'
      });
    }
    
    const rawData = fs.readFileSync(dataFile, 'utf-8');
    const allData = JSON.parse(rawData);
    
    const options = {
      链路: [...new Set(allData.map(row => row['链路']).filter(Boolean))].sort(),
      学段: [...new Set(allData.map(row => row['学段']).filter(Boolean))].sort(),
      竞品: [...new Set(allData.map(row => row['竞品']).filter(Boolean))].sort(),
      学科: [...new Set(allData.map(row => row['学科']).filter(Boolean))].sort()
    };
    
    res.json({
      options,
      total: allData.length
    });
  } catch (err) {
    console.error('API error:', err);
    res.status(500).json({ error: err.message });
  }
}
