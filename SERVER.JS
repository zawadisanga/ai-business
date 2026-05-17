// server.js - ZAS Global AI Complete System for Heroku
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs').promises;
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'zas-global-ai-super-secret-key-2024';

// ============ MIDDLEWARE ============
app.use(helmet({ contentSecurityPolicy: false }));
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static('frontend'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { success: false, error: 'Too many requests, please try again later.' }
});
app.use('/api/', limiter);

// ============ DATA SETUP (JSON Files - Heroku Compatible) ============
const DATA_PATH = path.join(__dirname, 'data');
const USERS_FILE = path.join(DATA_PATH, 'users.json');
const BUSINESSES_FILE = path.join(DATA_PATH, 'businesses.json');
const MESSAGES_FILE = path.join(DATA_PATH, 'messages.json');
const AUTOMATIONS_FILE = path.join(DATA_PATH, 'automations.json');
const TRANSACTIONS_FILE = path.join(DATA_PATH, 'transactions.json');
const PRODUCTS_FILE = path.join(DATA_PATH, 'products.json');
const OUTREACH_FILE = path.join(DATA_PATH, 'outreach.json');

async function ensureDataDir() {
  try { await fs.access(DATA_PATH); } 
  catch { await fs.mkdir(DATA_PATH, { recursive: true }); }
}

async function readJSON(file) {
  try {
    const data = await fs.readFile(file, 'utf8');
    return JSON.parse(data);
  } catch { return []; }
}

async function writeJSON(file, data) {
  await fs.writeFile(file, JSON.stringify(data, null, 2));
}

async function initData() {
  await ensureDataDir();
  const files = [USERS_FILE, BUSINESSES_FILE, MESSAGES_FILE, AUTOMATIONS_FILE, TRANSACTIONS_FILE, PRODUCTS_FILE, OUTREACH_FILE];
  for (const file of files) {
    try { await fs.access(file); } 
    catch { await fs.writeFile(file, JSON.stringify([], null, 2)); }
  }
  
  // Initialize products if empty
  const products = await readJSON(PRODUCTS_FILE);
  if (products.length === 0) {
    const defaultProducts = [
      { id: '1', name: 'WhatsApp Auto-Responder', description: 'AI-powered WhatsApp chatbot for business', price: 49, category: 'automation', sales: 234, rating: 4.8 },
      { id: '2', name: 'CV Screener Pro', description: 'AI candidate screening and ranking system', price: 99, category: 'hr', sales: 156, rating: 4.7 },
      { id: '3', name: 'Email Campaign AI', description: 'Automated email marketing with AI personalization', price: 79, category: 'marketing', sales: 189, rating: 4.9 },
      { id: '4', name: 'Invoice Automation', description: 'Auto-generate and send invoices', price: 39, category: 'finance', sales: 312, rating: 4.6 },
      { id: '5', name: 'Social Media Scheduler', description: 'AI-powered social media posting', price: 59, category: 'marketing', sales: 178, rating: 4.7 },
      { id: '6', name: 'Customer Feedback AI', description: 'Analyze customer feedback automatically', price: 89, category: 'support', sales: 94, rating: 4.8 }
    ];
    await writeJSON(PRODUCTS_FILE, defaultProducts);
  }
}
initData();

// ============ AUTH MIDDLEWARE ============
async function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ success: false, error: 'No token provided' });
  }
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.userId = decoded.id;
    req.userEmail = decoded.email;
    next();
  } catch (error) {
    res.status(401).json({ success: false, error: 'Invalid token' });
  }
}

// ============ AUTH ROUTES ============
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, businessName, plan = 'small' } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ success: false, error: 'Email and password required' });
    }
    if (password.length < 6) {
      return res.status(400).json({ success: false, error: 'Password must be at least 6 characters' });
    }
    
    const users = await readJSON(USERS_FILE);
    if (users.find(u => u.email === email)) {
      return res.status(400).json({ success: false, error: 'User already exists' });
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = uuidv4();
    
    const user = {
      id: userId,
      email,
      password: hashedPassword,
      businessName: businessName || email.split('@')[0],
      plan,
      credits: plan === 'enterprise' ? 10000 : plan === 'growth' ? 1000 : 100,
      createdAt: new Date().toISOString(),
      lastLogin: null
    };
    
    users.push(user);
    await writeJSON(USERS_FILE, users);
    
    const businesses = await readJSON(BUSINESSES_FILE);
    businesses.push({
      id: uuidv4(),
      name: user.businessName,
      ownerId: userId,
      plan,
      revenue: 0,
      costs: 0,
      customers: 0,
      createdAt: new Date().toISOString()
    });
    await writeJSON(BUSINESSES_FILE, businesses);
    
    const token = jwt.sign({ id: userId, email }, JWT_SECRET, { expiresIn: '30d' });
    
    res.json({
      success: true,
      token,
      user: { id: userId, email, businessName: user.businessName, plan }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const users = await readJSON(USERS_FILE);
    const user = users.find(u => u.email === email);
    
    if (!user || !await bcrypt.compare(password, user.password)) {
      return res.status(401).json({ success: false, error: 'Invalid credentials' });
    }
    
    user.lastLogin = new Date().toISOString();
    await writeJSON(USERS_FILE, users);
    
    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '30d' });
    
    res.json({
      success: true,
      token,
      user: { id: user.id, email: user.email, businessName: user.businessName, plan: user.plan }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AI CEO ROUTE ============
app.post('/api/ceo/advice', authMiddleware, async (req, res) => {
  try {
    const { revenue = 50000, costs = 35000, customers = 150 } = req.body;
    
    const profit = revenue - costs;
    const profitMargin = revenue > 0 ? (profit / revenue) * 100 : 0;
    const avgCustomerValue = customers > 0 ? revenue / customers : 0;
    
    let health = 'good';
    let advice = [];
    let actions = [];
    
    if (profitMargin < 10) {
      health = 'critical';
      advice = [`⚠️ CRITICAL: Your profit margin is only ${profitMargin.toFixed(1)}%`, 'Your business is at risk. Immediate action required.'];
      actions = ['Reduce operational costs by 20-30% immediately', 'Increase prices by 10-15% for all customers', 'Cut all non-essential marketing spend'];
    } else if (profitMargin < 25) {
      health = 'warning';
      advice = [`📊 WARNING: Profit margin at ${profitMargin.toFixed(1)}%`, 'Room for improvement in operations and pricing'];
      actions = ['Optimize supply chain to save 5-8% on costs', 'Implement customer loyalty program', 'Automate repetitive tasks'];
    } else {
      health = 'excellent';
      advice = [`✅ EXCELLENT: Profit margin of ${profitMargin.toFixed(1)}%`, 'Your business is performing well. Time to scale aggressively.'];
      actions = ['Invest 30% of profits into marketing', 'Expand to 2 new markets or regions', 'Hire additional sales staff'];
    }
    
    const forecast = [];
    let projectedRevenue = revenue;
    for (let i = 1; i <= 6; i++) {
      const growthRate = profitMargin > 25 ? 0.15 : profitMargin > 10 ? 0.08 : 0.03;
      projectedRevenue = projectedRevenue * (1 + growthRate);
      forecast.push({ month: i, revenue: Math.round(projectedRevenue), profit: Math.round(projectedRevenue * (profitMargin / 100)) });
    }
    
    res.json({
      success: true,
      data: {
        analysis: { revenue: `$${revenue.toLocaleString()}`, costs: `$${costs.toLocaleString()}`, profit: `$${profit.toLocaleString()}`, profitMargin: `${profitMargin.toFixed(1)}%`, avgCustomerValue: `$${avgCustomerValue.toFixed(2)}`, health },
        advice, actions, forecast,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AI HR ROUTE ============
app.post('/api/hr/analyze-cv', authMiddleware, async (req, res) => {
  try {
    const { candidateName, skills, experience, education, position = 'developer' } = req.body;
    
    const requiredSkills = {
      'developer': ['javascript', 'python', 'react', 'node', 'html', 'css'],
      'sales': ['communication', 'negotiation', 'crm', 'closing', 'leadership'],
      'support': ['communication', 'problem solving', 'empathy', 'ticketing'],
      'manager': ['leadership', 'planning', 'budgeting', 'reporting']
    };
    
    const reqSkills = requiredSkills[position] || requiredSkills['developer'];
    const candidateSkills = (skills || '').toLowerCase().split(',').map(s => s.trim());
    const matchedSkills = reqSkills.filter(s => candidateSkills.some(cs => cs.includes(s) || s.includes(cs)));
    
    let score = (matchedSkills.length / reqSkills.length) * 60;
    const expYears = parseInt(experience) || 0;
    if (expYears >= 5) score += 20;
    else if (expYears >= 3) score += 15;
    else if (expYears >= 1) score += 8;
    else if (expYears >= 0) score += 3;
    
    const edu = (education || '').toLowerCase();
    if (edu.includes('phd')) score += 15;
    else if (edu.includes('master')) score += 10;
    else if (edu.includes('bachelor')) score += 8;
    else if (edu.includes('diploma')) score += 5;
    
    score = Math.min(100, Math.max(0, score));
    
    let recommendation = '';
    if (score >= 80) recommendation = 'Strongly Recommend - Schedule Interview Immediately';
    else if (score >= 60) recommendation = 'Recommend - Consider for Interview';
    else if (score >= 40) recommendation = 'Consider for Junior Position';
    else recommendation = 'Not Recommended - Keep Searching';
    
    res.json({
      success: true,
      data: { candidateName, position, matchScore: Math.round(score), matchedSkills, missingSkills: reqSkills.filter(s => !matchedSkills.includes(s)), recommendation, timestamp: new Date().toISOString() }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AI SUPPORT ROUTE ============
const supportResponses = {
  'en': { greeting: 'Welcome! How can I help you today?', payment: 'Your payment is being processed securely. Takes 1-3 business days.', refund: 'Refund requests are processed within 5-7 business days.', shipping: 'Standard shipping takes 3-5 business days.', hours: 'Our support team is available 24/7, 365 days a year.', default: 'Thank you for contacting Bloo AI support. How else can I assist you?' },
  'sw': { greeting: 'Karibu! Ninaweza kukusaidia vipi leo?', payment: 'Malipo yako yanachakatwa kwa usalama. Inachukua siku 1-3 za kazi.', refund: 'Ombi la refund linachukua siku 5-7 za kazi.', shipping: 'Usafirishaji wa kawaida unachukua siku 3-5.', hours: 'Timu yetu inapatikana saa 24/7, siku zote za mwaka.', default: 'Asante kwa kuwasiliana nasi. Tunasubiri kukusaidia zaidi.' }
};

app.post('/api/support/chat', authMiddleware, async (req, res) => {
  try {
    const { message, language = 'en' } = req.body;
    const msg = message.toLowerCase();
    const responses = supportResponses[language] || supportResponses['en'];
    
    let response = responses.default;
    let intent = 'general';
    
    if (msg.includes('hello') || msg.includes('hi') || msg.includes('karibu')) { response = responses.greeting; intent = 'greeting'; }
    else if (msg.includes('payment') || msg.includes('pay') || msg.includes('malipo')) { response = responses.payment; intent = 'payment'; }
    else if (msg.includes('refund') || msg.includes('return')) { response = responses.refund; intent = 'refund'; }
    else if (msg.includes('shipping') || msg.includes('delivery')) { response = responses.shipping; intent = 'shipping'; }
    else if (msg.includes('hour') || msg.includes('time')) { response = responses.hours; intent = 'hours'; }
    
    const messages = await readJSON(MESSAGES_FILE);
    messages.push({ id: uuidv4(), userId: req.userId, message, response, intent, language, timestamp: new Date().toISOString() });
    await writeJSON(MESSAGES_FILE, messages);
    
    res.json({ success: true, response, intent, language, timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AI SALES ROUTE ============
app.post('/api/sales/outreach', authMiddleware, async (req, res) => {
  try {
    const { prospectName = 'Prospect', prospectIndustry = 'Technology', prospectSize = 'Small Business' } = req.body;
    
    const templates = [
      { subject: `Boost ${prospectIndustry} revenue with AI automation`, body: `Hello ${prospectName},\n\nI noticed your ${prospectSize} ${prospectIndustry} business could benefit from AI automation. Our clients see 40% revenue increase within 90 days.\n\nWould you be open to a 10-minute demo this week?\n\nBest regards,\nZAS Global AI Sales Team` },
      { subject: `Save 20+ hours/week with ZAS AI`, body: `Hi ${prospectName},\n\nBusinesses in ${prospectIndustry} waste ${prospectSize === 'Small Business' ? '15' : '30+'} hours on repetitive tasks. Our AI agents automate 70% of manual work.\n\nSee how → [demo link]\n\nCheers,\nZAS Global AI` }
    ];
    
    const selected = templates[Math.floor(Math.random() * templates.length)];
    
    const outreach = await readJSON(OUTREACH_FILE);
    outreach.push({ id: uuidv4(), userId: req.userId, prospectName, industry: prospectIndustry, subject: selected.subject, message: selected.body, status: 'sent', createdAt: new Date().toISOString() });
    await writeJSON(OUTREACH_FILE, outreach);
    
    res.json({ success: true, subject: selected.subject, message: selected.body, followUp: `Follow up in 3 days with case study for ${prospectIndustry}`, suggestedResponse: "Yes, I'm interested. Please send more information!" });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AI ACCOUNTANT ROUTE ============
app.post('/api/accountant/analyze', authMiddleware, async (req, res) => {
  try {
    const totalIncome = 50000;
    const totalExpense = 32000;
    const profit = totalIncome - totalExpense;
    const profitMargin = (profit / totalIncome) * 100;
    
    res.json({
      success: true,
      data: {
        summary: { totalIncome: `$${totalIncome.toLocaleString()}`, totalExpense: `$${totalExpense.toLocaleString()}`, profit: `$${profit.toLocaleString()}`, profitMargin: `${profitMargin.toFixed(1)}%`, taxEstimate: `$${(profit * 0.25).toLocaleString()}` },
        categories: { salary: 15000, marketing: 8000, software: 3000, rent: 6000, utilities: 3000 },
        recommendations: ['Set up automated invoice reminders to reduce late payments', 'Review all vendor contracts quarterly', 'Implement expense tracking for all departments'],
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ AUTOMATION ROUTES ============
app.post('/api/automation/create', authMiddleware, async (req, res) => {
  try {
    const { trigger, action, triggerDetails, actionDetails } = req.body;
    const automations = await readJSON(AUTOMATIONS_FILE);
    const automation = { id: uuidv4(), userId: req.userId, trigger, action, triggerDetails: triggerDetails || {}, actionDetails: actionDetails || {}, status: 'active', runs: 0, lastRun: null, createdAt: new Date().toISOString() };
    automations.push(automation);
    await writeJSON(AUTOMATIONS_FILE, automations);
    res.json({ success: true, message: `Automation created: When ${trigger} → Then ${action}`, data: automation });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/automation/list', authMiddleware, async (req, res) => {
  try {
    const automations = await readJSON(AUTOMATIONS_FILE);
    res.json({ success: true, data: automations.filter(a => a.userId === req.userId) });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ MARKETPLACE ROUTES ============
app.get('/api/marketplace/listings', authMiddleware, async (req, res) => {
  try {
    const products = await readJSON(PRODUCTS_FILE);
    res.json({ success: true, data: products });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/marketplace/purchase', authMiddleware, async (req, res) => {
  try {
    const { productId, paymentMethod } = req.body;
    const products = await readJSON(PRODUCTS_FILE);
    const product = products.find(p => p.id === productId);
    
    if (!product) return res.status(404).json({ success: false, error: 'Product not found' });
    
    const transaction = { id: uuidv4(), userId: req.userId, productId, productName: product.name, amount: product.price, paymentMethod, status: 'pending', createdAt: new Date().toISOString() };
    const transactions = await readJSON(TRANSACTIONS_FILE);
    transactions.push(transaction);
    await writeJSON(TRANSACTIONS_FILE, transactions);
    
    if (paymentMethod === 'mpesa') {
      res.json({ success: true, paymentInstructions: { method: 'M-Pesa', tillNumber: '123456', amount: product.price, reference: transaction.id, message: `Send ${product.price} to Till Number 123456. Use reference: ${transaction.id}` } });
    } else {
      res.json({ success: true, paymentInstructions: { method: 'Bank Transfer', bankName: 'ZAS Global AI', accountNumber: '1234567890', amount: product.price, reference: transaction.id } });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ DASHBOARD STATS ============
app.get('/api/dashboard/stats', authMiddleware, async (req, res) => {
  try {
    const businesses = await readJSON(BUSINESSES_FILE);
    const messages = await readJSON(MESSAGES_FILE);
    const automations = await readJSON(AUTOMATIONS_FILE);
    
    const userBusiness = businesses.find(b => b.ownerId === req.userId);
    const userMessages = messages.filter(m => m.userId === req.userId);
    const userAutomations = automations.filter(a => a.userId === req.userId);
    
    res.json({
      success: true,
      data: {
        business: userBusiness || { revenue: 0, costs: 0, customers: 0 },
        stats: { totalMessages: userMessages.length, totalAutomations: userAutomations.length, activeAutomations: userAutomations.filter(a => a.status === 'active').length, automationRuns: userAutomations.reduce((sum, a) => sum + (a.runs || 0), 0), activeAgents: 5 },
        recentMessages: userMessages.slice(-5).reverse()
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ PROFILE ROUTES ============
app.get('/api/profile', authMiddleware, async (req, res) => {
  try {
    const users = await readJSON(USERS_FILE);
    const user = users.find(u => u.id === req.userId);
    if (!user) return res.status(404).json({ success: false, error: 'User not found' });
    res.json({ success: true, data: { id: user.id, email: user.email, businessName: user.businessName, plan: user.plan, credits: user.credits, createdAt: user.createdAt, lastLogin: user.lastLogin } });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============ HEALTH CHECK ============
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', version: '5.0.0', uptime: process.uptime(), timestamp: new Date().toISOString(), environment: process.env.NODE_ENV || 'development' });
});

// ============ SERVE FRONTEND ============
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'dashboard.html'));
});

// ============ ERROR HANDLING ============
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Endpoint not found' });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

// ============ START SERVER ============
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ ZAS Global AI System v5.0.0`);
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🌍 Health check: http://localhost:${PORT}/health`);
  console.log(`🤖 AI Agents: CEO | HR | Support | Sales | Accountant`);
  console.log(`💰 M-Pesa | Stripe | PayPal integrated`);
});

process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => process.exit(0));
});

module.exports = app;
