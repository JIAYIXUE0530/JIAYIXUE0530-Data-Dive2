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
    const { page = 1, pageSize = 100 } = req.query;
    const pageNum = parseInt(page);
    const size = parseInt(pageSize);
    
    const dataDir = path.join(process.cwd(), 'public', 'data');
    const dataFile = path.join(dataDir, 'database.json');
    
    if (!fs.existsSync(dataFile)) {
      return res.json({ 
        data: [], 
        total: 0, 
        page: pageNum, 
        totalPages: 0,
        message: 'No data file found. Please upload data first.' 
      });
    }
    
    const rawData = fs.readFileSync(dataFile, 'utf-8');
    const allData = JSON.parse(rawData);
    
    const total = allData.length;
    const totalPages = Math.ceil(total / size);
    const startIndex = (pageNum - 1) * size;
    const endIndex = startIndex + size;
    const paginatedData = allData.slice(startIndex, endIndex);
    
    const sanitizedData = paginatedData.map(row => {
      const sanitizedRow = {};
      for (const [key, value] of Object.entries(row)) {
        if (typeof value === 'number') {
          if (Number.isNaN(value) || !Number.isFinite(value)) {
            sanitizedRow[key] = null;
          } else {
            sanitizedRow[key] = value;
          }
        } else {
          sanitizedRow[key] = value;
        }
      }
      return sanitizedRow;
    });
    
    res.json({
      data: sanitizedData,
      total,
      page: pageNum,
      totalPages
    });
  } catch (err) {
    console.error('API error:', err);
    res.status(500).json({ error: err.message });
  }
}
