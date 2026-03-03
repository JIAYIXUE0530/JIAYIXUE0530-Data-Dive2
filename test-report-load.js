import fetch from 'node-fetch';

async function testReportLoad() {
  try {
    console.log('Testing report loading...');
    
    // 测试1: 直接加载报告文件
    console.log('\n1. Testing direct report file load:');
    const reportResponse = await fetch('http://localhost:5174/outputs/reports/report-2026-02-28-daily-dashboard.json');
    console.log('Report file response status:', reportResponse.status);
    
    if (reportResponse.ok) {
      const reportData = await reportResponse.json();
      console.log('Report file loaded successfully');
      console.log('Report title:', reportData.meta.title);
      console.log('Total conclusions:', reportData.summary.total_conclusions);
    } else {
      console.log('Failed to load report file:', reportResponse.statusText);
    }
    
    // 测试2: 加载报告索引文件
    console.log('\n2. Testing reports index file load:');
    const indexResponse = await fetch('http://localhost:5174/outputs/reports/reports-index.json');
    console.log('Index file response status:', indexResponse.status);
    
    if (indexResponse.ok) {
      const indexData = await indexResponse.json();
      console.log('Index file loaded successfully');
      console.log('Number of reports:', indexData.reports.length);
      console.log('First report ID:', indexData.reports[0].id);
      console.log('First report filename:', indexData.reports[0].filename);
    } else {
      console.log('Failed to load index file:', indexResponse.statusText);
    }
    
  } catch (error) {
    console.error('Error during testing:', error);
  }
}

testReportLoad();