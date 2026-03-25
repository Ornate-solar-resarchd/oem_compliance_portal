#!/usr/bin/env python3
"""Generate 10 React JSX page files for UnityESS Technical Compliance Portal"""

import os

BASE_PATH = "src/pages"
os.makedirs(BASE_PATH, exist_ok=True)

# 1. Overview.jsx
OVERVIEW = '''import React, { useState } from 'react'
import { SHEETS, PROJECTS } from '../data/mockData'

export default function Overview() {
  const [selectedTab, setSelectedTab] = useState('All')

  const kpiCards = [
    { label: 'Active Projects', value: 6, icon: '📊' },
    { label: 'Sheets In Review', value: 7, icon: '📋' },
    { label: 'Pending Approvals', value: 7, icon: '⏳' },
    { label: 'Locked Sheets', value: 1, icon: '🔒' },
  ]

  const pendingQueue = SHEETS.filter(s => s.status !== 'Approved').slice(0, 8)
  const filteredQueue = selectedTab === 'All' ? pendingQueue : pendingQueue.filter(s => selectedTab === 'Pending' ? s.status === 'In Review' : s.status === 'Locked')

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Dashboard</h1>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {kpiCards.map((kpi, i) => (
          <div key={i} className="card" style={{ padding: '20px' }}>
            <div style={{ fontSize: '28px', marginBottom: '8px' }}>{kpi.icon}</div>
            <div style={{ fontSize: '24px', fontWeight: '600', color: 'var(--dark)', marginBottom: '4px' }}>{kpi.value}</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{kpi.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', borderBottom: `1px solid var(--border)`, paddingBottom: '12px' }}>
        {['All', 'Pending', 'Locked'].map(tab => (
          <button key={tab} onClick={() => setSelectedTab(tab)} className={selectedTab === tab ? 'btn btn-primary' : 'btn btn-ghost'} style={{ fontSize: '13px' }}>
            {tab}
          </button>
        ))}
      </div>

      {/* Pending Queue Table */}
      <div className="card" style={{ padding: '20px', overflowX: 'auto' }}>
        <h3 style={{ marginBottom: '16px', color: 'var(--dark)', fontSize: '16px', fontFamily: 'Chivo' }}>Pending Queue</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: `1px solid var(--border)` }}>
              <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Sheet #</th>
              <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Project</th>
              <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Model</th>
              <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Stage</th>
              <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Waiting</th>
            </tr>
          </thead>
          <tbody>
            {filteredQueue.map((sheet, i) => (
              <tr key={i} style={{ borderBottom: `1px solid var(--border)` }}>
                <td style={{ padding: '12px 0' }}><strong>#{sheet.number}</strong></td>
                <td style={{ padding: '12px 0' }}>{sheet.project}</td>
                <td style={{ padding: '12px 0' }}>{sheet.model}</td>
                <td style={{ padding: '12px 0' }}><span className={`badge badge-${sheet.status === 'In Review' ? 'pending' : 'fail'}`}>{sheet.status}</span></td>
                <td style={{ padding: '12px 0', color: 'var(--muted)' }}>{Math.floor(Math.random() * 72)}h</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recent Activity Feed */}
      <div className="card" style={{ padding: '20px', marginTop: '24px' }}>
        <h3 style={{ marginBottom: '16px', color: 'var(--dark)', fontSize: '16px', fontFamily: 'Chivo' }}>Recent Activity</h3>
        {SHEETS.slice(0, 5).map((sheet, i) => (
          <div key={i} style={{ padding: '12px 0', borderBottom: i < 4 ? `1px solid var(--border)` : 'none', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '13px', color: 'var(--dark)' }}>Sheet #{sheet.number} — {sheet.project}</div>
              <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>{sheet.status}</div>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>2h ago</div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# 2. Projects.jsx
PROJECTS_PAGE = '''import React, { useState } from 'react'
import { PROJECTS, SHEETS } from '../data/mockData'

export default function Projects() {
  const [selectedProject, setSelectedProject] = useState(null)

  const kpiCards = [
    { label: 'Total Projects', value: 6, icon: '📊' },
    { label: 'Active', value: 6, icon: '✅' },
    { label: 'Locked Sheets', value: 1, icon: '🔒' },
    { label: 'Pending Sheets', value: 5, icon: '⏳' },
  ]

  const selectedProjectData = selectedProject ? PROJECTS.find(p => p.id === selectedProject) : null
  const projectSheets = selectedProjectData ? SHEETS.filter(s => s.project === selectedProjectData.name) : []

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Projects</h1>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {kpiCards.map((kpi, i) => (
          <div key={i} className="card" style={{ padding: '20px' }}>
            <div style={{ fontSize: '28px', marginBottom: '8px' }}>{kpi.icon}</div>
            <div style={{ fontSize: '24px', fontWeight: '600', color: 'var(--dark)' }}>{kpi.value}</div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{kpi.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 320px', gap: '24px' }}>
        {/* Projects Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
          {PROJECTS.map((project) => (
            <div key={project.id} className="card" onClick={() => setSelectedProject(project.id)} style={{ padding: '20px', cursor: 'pointer', border: selectedProject === project.id ? '2px solid var(--orange)' : '1px solid var(--border)', transition: 'all 0.2s' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                <div>
                  <h3 style={{ color: 'var(--dark)', fontSize: '15px', fontWeight: '600', margin: '0' }}>{project.name}</h3>
                  <p style={{ color: 'var(--muted)', fontSize: '12px', margin: '4px 0 0' }}>{project.client}</p>
                </div>
                <span className={`badge badge-${project.type === 'Residential' ? 'blue' : 'orange'}`}>{project.type}</span>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '12px' }}>
                <div>{project.capacity} kWh / {project.kw} kW</div>
                <div>{project.location}</div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '4px' }}>Progress</div>
                <div style={{ height: '6px', backgroundColor: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', backgroundColor: 'var(--orange)', width: `${project.progress || 45}%` }}></div>
                </div>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--dark)', paddingTop: '12px', borderTop: '1px solid var(--border)' }}>
                {SHEETS.filter(s => s.project === project.name).length} sheets
              </div>
            </div>
          ))}
        </div>

        {/* Right Panel */}
        {selectedProjectData && (
          <div className="card" style={{ padding: '20px', height: 'fit-content' }}>
            <h3 style={{ color: 'var(--dark)', fontSize: '14px', fontWeight: '600', marginBottom: '16px' }}>Sheets</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {projectSheets.map((sheet, i) => (
                <div key={i} style={{ padding: '8px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)', fontSize: '12px' }}>
                  <div style={{ fontWeight: '600', color: 'var(--dark)' }}>#{sheet.number}</div>
                  <div style={{ color: 'var(--muted)', marginTop: '2px' }}>{sheet.model}</div>
                  <span className={`badge badge-${sheet.status === 'Approved' ? 'pass' : 'pending'}`} style={{ marginTop: '4px' }}>{sheet.status}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
'''

# 3. OEMLibrary.jsx
OEM_LIBRARY = '''import React, { useState, useMemo } from 'react'
import { OEMS } from '../data/mockData'

export default function OEMLibrary() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('All')
  const [approvedOnly, setApprovedOnly] = useState(false)

  const countryFlags = {
    'China': '🇨🇳',
    'Germany': '🇩🇪',
    'Japan': '🇯🇵',
    'USA': '🇺🇸',
    'India': '🇮🇳',
  }

  const filtered = useMemo(() => {
    return OEMS.filter(oem => {
      const matchesSearch = oem.name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = categoryFilter === 'All' || oem.category === categoryFilter
      const matchesApproved = !approvedOnly || oem.approved
      return matchesSearch && matchesCategory && matchesApproved
    })
  }, [searchTerm, categoryFilter, approvedOnly])

  const categories = ['All', ...new Set(OEMS.map(o => o.category))]

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>OEM Library</h1>

      {/* Search & Filters */}
      <div className="card" style={{ padding: '16px', marginBottom: '24px' }}>
        <input type="text" placeholder="Search OEMs..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', marginBottom: '12px', fontSize: '13px' }} />
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '12px' }}>
          {categories.map(cat => (
            <button key={cat} onClick={() => setCategoryFilter(cat)} className={categoryFilter === cat ? 'btn btn-primary' : 'btn btn-outline'} style={{ fontSize: '12px' }}>
              {cat}
            </button>
          ))}
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', cursor: 'pointer' }}>
          <input type="checkbox" checked={approvedOnly} onChange={(e) => setApprovedOnly(e.target.checked)} />
          <span>Approved only</span>
        </label>
      </div>

      {/* OEM Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
        {filtered.map((oem) => (
          <div key={oem.id} className="card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
              <div>
                <h3 style={{ color: 'var(--dark)', fontSize: '15px', fontWeight: '600', margin: '0' }}>{oem.name}</h3>
                <p style={{ color: 'var(--muted)', fontSize: '12px', margin: '4px 0 0' }}>{countryFlags[oem.country] || '🌍'} {oem.country}</p>
              </div>
              <span className={`badge badge-${oem.approved ? 'pass' : 'pending'}`}>{oem.approved ? 'Approved' : 'Pending'}</span>
            </div>

            {/* Score Ring */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <svg width="80" height="80" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx="40" cy="40" r="36" fill="none" stroke="var(--border)" strokeWidth="4" />
                <circle cx="40" cy="40" r="36" fill="none" stroke={oem.score >= 80 ? 'var(--orange)' : oem.score >= 60 ? '#FFA500' : '#FF6B6B'} strokeWidth="4" strokeDasharray={`${(oem.score / 100) * 226.2} 226.2`} strokeLinecap="round" />
                <text x="40" y="45" textAnchor="middle" fill="var(--dark)" fontSize="18" fontWeight="600">{oem.score}%</text>
              </svg>
            </div>

            <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '12px' }}>
              <div>{oem.modelCount} models</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# 4. Components.jsx
COMPONENTS_PAGE = '''import React, { useState, useMemo } from 'react'
import { MODELS, PARAMETERS } from '../data/mockData'

export default function Components() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedModel, setSelectedModel] = useState(null)

  const filtered = useMemo(() => {
    return MODELS.filter(m => m.oem.toLowerCase().includes(searchTerm.toLowerCase()) || m.model.toLowerCase().includes(searchTerm.toLowerCase()))
  }, [searchTerm])

  const modelDetail = selectedModel ? MODELS.find(m => m.id === selectedModel) : null
  const modelParams = modelDetail ? PARAMETERS.filter(p => p.modelId === modelDetail.id) : []

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Components</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '40% 1fr', gap: '24px' }}>
        {/* Left: Components Table */}
        <div className="card" style={{ padding: '20px', height: 'fit-content' }}>
          <input type="text" placeholder="Search models..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', marginBottom: '16px', fontSize: '13px' }} />
          <div style={{ overflowY: 'auto', maxHeight: '600px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: `1px solid var(--border)` }}>
                  <th style={{ textAlign: 'left', padding: '8px 0', color: 'var(--muted)', fontWeight: '500' }}>OEM</th>
                  <th style={{ textAlign: 'left', padding: '8px 0', color: 'var(--muted)', fontWeight: '500' }}>Model</th>
                  <th style={{ textAlign: 'left', padding: '8px 0', color: 'var(--muted)', fontWeight: '500' }}>Fill%</th>
                  <th style={{ textAlign: 'left', padding: '8px 0', color: 'var(--muted)', fontWeight: '500' }}>Score</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((model) => (
                  <tr key={model.id} onClick={() => setSelectedModel(model.id)} style={{ borderBottom: `1px solid var(--border)`, cursor: 'pointer', backgroundColor: selectedModel === model.id ? 'var(--bg)' : 'transparent', padding: '6px 0' }}>
                    <td style={{ padding: '8px 0' }}>{model.oem}</td>
                    <td style={{ padding: '8px 0', fontSize: '11px' }}>{model.model}</td>
                    <td style={{ padding: '8px 0' }}>{model.fill}%</td>
                    <td style={{ padding: '8px 0', fontWeight: '600', color: model.score >= 80 ? 'var(--orange)' : '#FF6B6B' }}>{model.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Parameter Details */}
        {modelDetail && (
          <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ color: 'var(--dark)', fontSize: '15px', fontWeight: '600', marginBottom: '20px' }}>{modelDetail.oem} {modelDetail.model}</h3>

            {['Electrical', 'Thermal', 'Safety', 'Origin'].map(section => {
              const sectionParams = modelParams.filter(p => p.section === section)
              return sectionParams.length > 0 && (
                <div key={section} style={{ marginBottom: '24px' }}>
                  <h4 style={{ color: 'var(--muted)', fontSize: '12px', fontWeight: '600', marginBottom: '12px', textTransform: 'uppercase' }}>{section}</h4>
                  {sectionParams.map((param, i) => (
                    <div key={i} style={{ padding: '12px', marginBottom: '8px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                        <span style={{ fontSize: '12px', color: 'var(--dark)', fontWeight: '500' }}>{param.name}</span>
                        <span className={`badge badge-${param.status === 'Pass' ? 'pass' : 'pending'}`} style={{ fontSize: '10px' }}>{param.status}</span>
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' }}>OEM: {param.oemValue}</div>
                      <div style={{ height: '4px', backgroundColor: 'var(--border)', borderRadius: '2px', marginBottom: '6px' }}>
                        <div style={{ height: '100%', backgroundColor: 'var(--orange)', width: `${param.confidence}%` }}></div>
                      </div>
                      <span style={{ fontSize: '10px', backgroundColor: 'var(--border)', padding: '2px 6px', borderRadius: '3px', color: 'var(--muted)' }}>{param.source}</span>
                    </div>
                  ))}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
'''

# 5. ComplianceBuilder.jsx
COMPLIANCE_BUILDER = '''import React, { useState } from 'react'
import { SHEETS, PARAMETERS } from '../data/mockData'

export default function ComplianceBuilder() {
  const [selectedSheet, setSelectedSheet] = useState(SHEETS[0]?.id || null)
  const [waivedParams, setWaivedParams] = useState([])

  const sheetData = selectedSheet ? SHEETS.find(s => s.id === selectedSheet) : null
  const sheetParams = sheetData ? PARAMETERS.filter(p => p.sheetId === sheetData.id) : []

  const passCount = sheetParams.filter(p => p.status === 'Pass' && !waivedParams.includes(p.id)).length
  const failCount = sheetParams.filter(p => p.status === 'Fail' && !waivedParams.includes(p.id)).length
  const waivedCount = waivedParams.length

  const hasFailures = failCount > 0

  const toggleWaive = (paramId) => {
    setWaivedParams(prev => prev.includes(paramId) ? prev.filter(id => id !== paramId) : [...prev, paramId])
  }

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Compliance Builder</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '40% 1fr', gap: '24px' }}>
        {/* Left Panel */}
        <div>
          {/* Form */}
          <div className="card" style={{ padding: '20px', marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Sheet</label>
            <select value={selectedSheet || ''} onChange={(e) => setSelectedSheet(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px', marginBottom: '16px' }}>
              {SHEETS.map(s => (
                <option key={s.id} value={s.id}>{s.number} — {s.project}</option>
              ))}
            </select>

            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Component Type</label>
            <select style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px', marginBottom: '16px' }}>
              <option>Inverter</option>
              <option>Battery</option>
            </select>

            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Model</label>
            <select style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px', marginBottom: '16px' }}>
              <option>GoodWe GW10K-DT</option>
              <option>SMA SB3.6</option>
            </select>

            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Template</label>
            <select style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px', marginBottom: '16px' }}>
              <option>Standard 2024</option>
              <option>Residential</option>
            </select>
          </div>

          {/* Donut Chart */}
          <div className="card" style={{ padding: '20px', textAlign: 'center' }}>
            <svg width="120" height="120" style={{ margin: '0 auto 16px' }}>
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border)" strokeWidth="12" />
              <circle cx="60" cy="60" r="50" fill="none" stroke="var(--orange)" strokeWidth="12" strokeDasharray={`${(passCount / (passCount + failCount + waivedCount)) * 314} 314`} />
            </svg>
            <div style={{ fontSize: '20px', fontWeight: '600', color: 'var(--dark)', marginBottom: '4px' }}>
              {passCount}/{passCount + failCount + waivedCount}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Parameters Pass</div>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '16px', flexWrap: 'wrap' }}>
              <span className="badge badge-pass">{passCount} Pass</span>
              <span className="badge badge-fail">{failCount} Fail</span>
              <span className="badge badge-waived">{waivedCount} Waived</span>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div>
          {hasFailures && (
            <div style={{ padding: '12px', backgroundColor: '#fff3cd', border: `1px solid #ffc107`, borderRadius: 'var(--radius)', marginBottom: '16px', fontSize: '12px', color: '#856404' }}>
              ⚠️ Compliance gate blocked: {failCount} mandatory parameter(s) failing
            </div>
          )}

          <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '16px' }}>Parameters</h3>
            {['Electrical', 'Thermal', 'Safety'].map(section => {
              const sectionParams = sheetParams.filter(p => p.section === section)
              return sectionParams.length > 0 && (
                <div key={section} style={{ marginBottom: '20px' }}>
                  <h4 style={{ fontSize: '11px', fontWeight: '600', color: 'var(--muted)', textTransform: 'uppercase', marginBottom: '12px' }}>{section}</h4>
                  {sectionParams.map((param) => (
                    <div key={param.id} style={{ padding: '12px', marginBottom: '8px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '12px', color: 'var(--dark)', fontWeight: '500', marginBottom: '4px' }}>{param.name}</div>
                        <div style={{ fontSize: '11px', color: 'var(--muted)' }}>OEM: {param.oemValue}</div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span className={`badge badge-${waivedParams.includes(param.id) ? 'waived' : param.status === 'Pass' ? 'pass' : 'fail'}`}>{waivedParams.includes(param.id) ? 'Waived' : param.status}</span>
                        {param.status === 'Fail' && (
                          <button onClick={() => toggleWaive(param.id)} className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 8px' }}>Waive</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )
            })}
          </div>

          <button className="btn btn-primary" disabled={hasFailures} style={{ width: '100%', marginTop: '16px', opacity: hasFailures ? 0.5 : 1, cursor: hasFailures ? 'not-allowed' : 'pointer' }}>
            Submit for Approval
          </button>
        </div>
      </div>
    </div>
  )
}
'''

# 6. ApprovalWorkflow.jsx
APPROVAL_WORKFLOW = '''import React, { useState } from 'react'
import { SHEETS, STAGE_LABELS } from '../data/mockData'

export default function ApprovalWorkflow() {
  const [selectedSheet, setSelectedSheet] = useState(SHEETS[0]?.id || null)
  const [comment, setComment] = useState('')

  const sheetData = selectedSheet ? SHEETS.find(s => s.id === selectedSheet) : null
  const currentStage = sheetData?.stage || 0

  const stages = ['Submitted', 'QA Review', 'Safety Review', 'Approval', 'Signed', 'Locked', 'Archived']
  const waitingTimeHours = Math.floor(Math.random() * 96)

  const getWaitingChip = (hours) => {
    let bgColor = '#d4edda'
    let textColor = '#155724'
    if (hours > 48) {
      bgColor = '#f8d7da'
      textColor = '#721c24'
    } else if (hours > 24) {
      bgColor = '#fff3cd'
      textColor = '#856404'
    }
    return { bgColor, textColor, label: hours < 24 ? `${hours}h (< 24h)` : hours < 48 ? `${hours}h (24-48h)` : `${hours}h (> 48h)` }
  }

  const chipStyle = getWaitingChip(waitingTimeHours)

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Approval Workflow</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '24px' }}>
        {/* Left Panel */}
        <div>
          {/* Pipeline Visualization */}
          <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '20px' }}>Workflow Pipeline</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
              {stages.map((stage, i) => (
                <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: i < currentStage ? 'var(--orange)' : i === currentStage ? 'transparent' : 'var(--border)', border: i === currentStage ? `2px solid var(--orange)` : 'none', margin: '0 auto 8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: '600', color: 'white' }}>
                    {i < currentStage ? '✓' : i + 1}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--muted)' }}>{stage}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Pending Queue */}
          <div className="card" style={{ padding: '20px', marginBottom: '24px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '16px' }}>Pending Queue</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <tbody>
                {SHEETS.filter(s => s.status !== 'Approved').slice(0, 5).map((sheet, i) => (
                  <tr key={i} style={{ borderBottom: i < 4 ? `1px solid var(--border)` : 'none' }}>
                    <td style={{ padding: '10px 0' }}>
                      <div style={{ fontWeight: '600', color: 'var(--dark)' }}>#{sheet.number}</div>
                      <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>{sheet.project}</div>
                    </td>
                    <td style={{ padding: '10px 0', textAlign: 'right' }}>
                      <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '4px', backgroundColor: Math.random() > 0.5 ? '#d4edda' : '#fff3cd', color: Math.random() > 0.5 ? '#155724' : '#856404' }}>
                        {Math.floor(Math.random() * 72)}h
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Workflow History */}
          <div className="card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '16px' }}>History</h3>
            {[
              { step: 'Submitted', actor: 'You', time: '2h ago', comment: 'Initial submission' },
              { step: 'QA Review', actor: 'Priya Kumar', time: '1h ago', comment: 'Passed QA checks' },
            ].map((entry, i) => (
              <div key={i} style={{ padding: '12px 0', borderBottom: i === 0 ? `1px solid var(--border)` : 'none' }}>
                <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--dark)' }}>{entry.step}</div>
                <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>by {entry.actor} · {entry.time}</div>
                <div style={{ fontSize: '11px', color: 'var(--dark)', marginTop: '4px', fontStyle: 'italic' }}>"{entry.comment}"</div>
                <div style={{ fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>Sig: abc123def...</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel */}
        <div>
          <div className="card" style={{ padding: '20px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Select Sheet</label>
            <select value={selectedSheet || ''} onChange={(e) => setSelectedSheet(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px', marginBottom: '16px' }}>
              {SHEETS.map(s => (
                <option key={s.id} value={s.id}>{s.number} — {s.project}</option>
              ))}
            </select>

            {sheetData && (
              <>
                <div style={{ padding: '12px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)', marginBottom: '16px', fontSize: '12px' }}>
                  <div style={{ color: 'var(--muted)', marginBottom: '4px' }}>Status</div>
                  <div style={{ fontWeight: '600', color: 'var(--dark)' }}>{sheetData.status}</div>
                  <div style={{ marginTop: '8px', color: 'var(--muted)' }}>Waiting time</div>
                  <span style={{ display: 'inline-block', marginTop: '4px', padding: '4px 8px', borderRadius: '4px', backgroundColor: chipStyle.bgColor, color: chipStyle.textColor, fontSize: '11px' }}>
                    ⏱️ {chipStyle.label}
                  </span>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Comment</label>
                  <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Add a comment..." style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px', minHeight: '80px', fontFamily: 'Chivo', resize: 'vertical' }}></textarea>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="btn btn-primary" style={{ flex: 1, fontSize: '12px' }}>Approve</button>
                  <button className="btn btn-outline" style={{ flex: 1, fontSize: '12px' }}>Reject</button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
'''

# 7. Compare.jsx
COMPARE = '''import React, { useState } from 'react'
import { MODELS, PARAMETERS } from '../data/mockData'

export default function Compare() {
  const [componentType, setComponentType] = useState('Inverter')
  const [selectedModels, setSelectedModels] = useState([MODELS[0]?.id, MODELS[1]?.id].filter(Boolean))
  const [parameterFilter, setParameterFilter] = useState('All')

  const availableModels = MODELS.filter(m => m.type === componentType)
  const comparisonModels = availableModels.filter(m => selectedModels.includes(m.id))
  const comparisonParams = PARAMETERS.filter(p => comparisonModels.some(m => m.id === p.modelId))

  const toggleModel = (modelId) => {
    setSelectedModels(prev => prev.includes(modelId) ? prev.filter(id => id !== modelId) : [...prev, modelId])
  }

  const getParamValue = (modelId, paramName) => {
    const param = PARAMETERS.find(p => p.modelId === modelId && p.name === paramName)
    return param ? parseFloat(param.oemValue) : 0
  }

  const uniqueParams = [...new Set(comparisonParams.map(p => p.name))]
  const paramsBySection = {}
  uniqueParams.forEach(name => {
    const param = comparisonParams.find(p => p.name === name)
    if (param) {
      if (!paramsBySection[param.section]) paramsBySection[param.section] = []
      paramsBySection[param.section].push(name)
    }
  })

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Component Comparison</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '40% 1fr', gap: '24px' }}>
        {/* Left Panel */}
        <div className="card" style={{ padding: '20px', height: 'fit-content' }}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Component Type</label>
          <select value={componentType} onChange={(e) => { setComponentType(e.target.value); setSelectedModels([]); }} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px', marginBottom: '16px' }}>
            <option>Inverter</option>
            <option>Battery</option>
            <option>Controller</option>
          </select>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '12px' }}>Select Models</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
            {availableModels.map(m => (
              <button key={m.id} onClick={() => toggleModel(m.id)} className={selectedModels.includes(m.id) ? 'btn btn-primary' : 'btn btn-outline'} style={{ fontSize: '11px', padding: '4px 8px' }}>
                {m.oem}
              </button>
            ))}
          </div>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Filter Parameters</label>
          <select value={parameterFilter} onChange={(e) => setParameterFilter(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '13px' }}>
            <option>All</option>
            <option>Electrical</option>
            <option>Thermal</option>
            <option>Safety</option>
          </select>
        </div>

        {/* Right Panel: Comparison Matrix */}
        <div className="card" style={{ padding: '20px', overflowX: 'auto' }}>
          {selectedModels.length > 0 ? (
            <>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: `2px solid var(--border)` }}>
                    <th style={{ textAlign: 'left', padding: '12px', color: 'var(--muted)', fontWeight: '600' }}>Parameter</th>
                    {comparisonModels.map(m => (
                      <th key={m.id} style={{ textAlign: 'center', padding: '12px', color: 'var(--dark)', fontWeight: '600' }}>
                        <div>{m.oem}</div>
                        <div style={{ fontSize: '11px', fontWeight: '400', color: 'var(--muted)' }}>{m.model}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(paramsBySection).map(([section, params]) => (
                    <React.Fragment key={section}>
                      <tr style={{ backgroundColor: 'var(--bg)' }}>
                        <td colSpan={comparisonModels.length + 1} style={{ padding: '8px 12px', fontSize: '11px', fontWeight: '600', color: 'var(--muted)', textTransform: 'uppercase' }}>{section}</td>
                      </tr>
                      {params.map(param => {
                        const values = comparisonModels.map(m => getParamValue(m.id, param))
                        const maxVal = Math.max(...values)
                        const minVal = Math.min(...values)
                        return (
                          <tr key={param} style={{ borderBottom: `1px solid var(--border)` }}>
                            <td style={{ padding: '10px 12px', color: 'var(--dark)' }}>{param}</td>
                            {comparisonModels.map((m, i) => (
                              <td key={m.id} style={{ padding: '10px 12px', textAlign: 'center', backgroundColor: values[i] === maxVal ? '#e8f5e9' : values[i] === minVal ? '#ffebee' : 'transparent' }}>
                                {values[i]}
                              </td>
                            ))}
                          </tr>
                        )
                      })}
                    </React.Fragment>
                  ))}
                  <tr style={{ borderTop: `2px solid var(--border)`, backgroundColor: 'var(--bg)' }}>
                    <td style={{ padding: '12px', fontWeight: '600', color: 'var(--dark)' }}>Overall Score</td>
                    {comparisonModels.map(m => (
                      <td key={m.id} style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: 'var(--orange)' }}>
                        🏆 {m.score}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--muted)', padding: '40px 20px' }}>
              Select at least one model to compare
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
'''

# 8. Documents.jsx
DOCUMENTS = '''import React, { useState } from 'react'
import { SHEETS } from '../data/mockData'

export default function Documents() {
  const [docType, setDocType] = useState('Compliance Sheet')
  const [selectedSheet, setSelectedSheet] = useState(SHEETS[0]?.id || null)
  const [format, setFormat] = useState('PDF')

  const recentExports = [
    { id: 1, type: 'Compliance Sheet', sheet: 'SS-001', format: 'PDF', size: '2.4 MB', status: 'ready', hash: 'a1b2c3d4e5f6g7h8...' },
    { id: 2, type: 'Comparison Report', sheet: 'SS-002', format: 'Excel', size: '1.8 MB', status: 'ready', hash: 'x9y8z7w6v5u4t3s2...' },
    { id: 3, type: 'Customer Proposal', sheet: 'SS-003', format: 'PPTX', size: '5.2 MB', status: 'processing', hash: null },
  ]

  const kpiCards = [
    { label: 'Total Exports', value: 24, icon: '📄' },
    { label: 'Pending', value: 3, icon: '⏳' },
    { label: 'Ready', value: 21, icon: '✅' },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Documents & Export</h1>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {kpiCards.map((kpi, i) => (
          <div key={i} className="card" style={{ padding: '16px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>{kpi.icon}</div>
            <div style={{ fontSize: '20px', fontWeight: '600', color: 'var(--dark)' }}>{kpi.value}</div>
            <div style={{ fontSize: '11px', color: 'var(--muted)' }}>{kpi.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '40% 1fr', gap: '24px' }}>
        {/* Left: Generate Form */}
        <div className="card" style={{ padding: '20px', height: 'fit-content' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '16px' }}>Generate Document</h3>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Document Type</label>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            {['Compliance Sheet', 'Comparison Report', 'Customer Proposal'].map(type => (
              <button key={type} onClick={() => setDocType(type)} className={docType === type ? 'btn btn-primary' : 'btn btn-outline'} style={{ fontSize: '11px', padding: '6px 10px' }}>
                {type}
              </button>
            ))}
          </div>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Sheet</label>
          <select value={selectedSheet || ''} onChange={(e) => setSelectedSheet(e.target.value)} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px', marginBottom: '16px' }}>
            {SHEETS.map(s => (
              <option key={s.id} value={s.id}>{s.number} — {s.project}</option>
            ))}
          </select>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Format</label>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {['PDF', 'Excel', 'PPTX'].map(fmt => (
              <button key={fmt} onClick={() => setFormat(fmt)} className={format === fmt ? 'btn btn-primary' : 'btn btn-outline'} style={{ fontSize: '11px', padding: '6px 10px' }}>
                {fmt}
              </button>
            ))}
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', marginBottom: '8px', cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Include signatures</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', marginBottom: '16px', cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Include watermark</span>
          </label>

          <button className="btn btn-primary" style={{ width: '100%' }}>Generate & Download</button>
        </div>

        {/* Right: Recent Exports */}
        <div className="card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)', marginBottom: '16px' }}>Recent Exports</h3>
          {recentExports.map((exp, i) => (
            <div key={i} style={{ padding: '12px', marginBottom: '12px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                <div>
                  <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--dark)' }}>{exp.type}</div>
                  <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>{exp.sheet} · {exp.size}</div>
                </div>
                <span className={`badge badge-${exp.status === 'ready' ? 'pass' : 'pending'}`} style={{ fontSize: '10px' }}>
                  {exp.status === 'processing' ? '⏳ Processing...' : '✅ Ready'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '10px', padding: '2px 6px', backgroundColor: 'var(--border)', borderRadius: '3px', color: 'var(--muted)' }}>{exp.format}</span>
                {exp.status === 'ready' && (
                  <button className="btn btn-ghost" style={{ fontSize: '10px', padding: '2px 6px' }}>⬇️ Download</button>
                )}
              </div>
              {exp.hash && (
                <div style={{ fontSize: '9px', color: 'var(--muted)', marginTop: '6px', wordBreak: 'break-all' }}>SHA-256: {exp.hash}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
'''

# 9. CustomerPortal.jsx
CUSTOMER_PORTAL = '''import React, { useState } from 'react'
import { SHEETS } from '../data/mockData'

export default function CustomerPortal() {
  const [signedSheets, setSignedSheets] = useState({})
  const [signatoryName, setSignatoryName] = useState('')

  const project = {
    name: 'Chennai Solar Residential',
    client: 'Acme Solar Ltd.',
    capacity: '10 kWh / 5 kW',
  }

  const handleSignOff = (sheetId) => {
    if (!signatoryName.trim()) {
      alert('Please enter your name')
      return
    }
    setSignedSheets(prev => ({ ...prev, [sheetId]: { name: signatoryName, time: new Date().toLocaleString() } }))
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg)' }}>
      {/* Minimal Header */}
      <div style={{ padding: '16px 24px', backgroundColor: 'var(--surface)', borderBottom: `1px solid var(--border)`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--dark)', fontFamily: 'Chivo' }}>UnityESS</div>
          <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--orange)', fontFamily: 'Chivo' }}>TCP</div>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--muted)', padding: '4px 8px', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
          Token: 6d9a2c1f valid until 2026-03-20
        </div>
      </div>

      {/* Project Banner */}
      <div style={{ background: 'linear-gradient(135deg, var(--orange), #FF8C42)', padding: '24px', color: 'white' }}>
        <h1 style={{ margin: '0', fontSize: '28px', fontWeight: '700', fontFamily: 'Chivo' }}>{project.name}</h1>
        <p style={{ margin: '8px 0 0', fontSize: '14px', opacity: 0.9 }}>{project.client}</p>
        <p style={{ margin: '4px 0 0', fontSize: '13px', opacity: 0.85 }}>{project.capacity}</p>
      </div>

      {/* Content */}
      <div style={{ padding: '24px' }}>
        {SHEETS.slice(0, 3).map((sheet) => (
          <div key={sheet.id} className="card" style={{ marginBottom: '24px', padding: '20px' }}>
            <h2 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>
              Sheet #{sheet.number} — {sheet.model}
            </h2>

            <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)' }}>
              <span className={`badge badge-${sheet.status === 'Approved' ? 'pass' : 'pending'}`}>{sheet.status}</span>
            </div>

            {/* Compliance Results Table */}
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', marginBottom: '20px' }}>
              <thead>
                <tr style={{ borderBottom: `1px solid var(--border)` }}>
                  <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Parameter</th>
                  <th style={{ textAlign: 'center', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Status</th>
                  <th style={{ textAlign: 'center', padding: '10px 0', color: 'var(--muted)', fontWeight: '500' }}>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: `1px solid var(--border)` }}>
                  <td style={{ padding: '10px 0' }}>Efficiency Rating</td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}><span className="badge badge-pass">Pass</span></td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}>96.5%</td>
                </tr>
                <tr style={{ borderBottom: `1px solid var(--border)` }}>
                  <td style={{ padding: '10px 0' }}>Safety Certification</td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}><span className="badge badge-pass">Pass</span></td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}>IEC 61010</td>
                </tr>
                <tr>
                  <td style={{ padding: '10px 0' }}>Thermal Rating</td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}><span className="badge badge-pass">Pass</span></td>
                  <td style={{ padding: '10px 0', textAlign: 'center' }}>-40 to +60°C</td>
                </tr>
              </tbody>
            </table>

            {!signedSheets[sheet.id] && (
              <button className="btn btn-primary" style={{ width: '100%', marginBottom: '20px' }}>
                📥 Download Report
              </button>
            )}

            {/* Sign-Off Zone */}
            <div style={{ padding: '16px', backgroundColor: '#fff9e6', border: `1px solid #ffe082`, borderRadius: 'var(--radius)' }}>
              <h3 style={{ margin: '0 0 12px', fontSize: '13px', fontWeight: '600', color: 'var(--dark)' }}>Digital Sign-Off</h3>

              {!signedSheets[sheet.id] ? (
                <>
                  <p style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '12px', lineHeight: '1.6' }}>
                    By signing below, you acknowledge that you have reviewed the compliance results and accept this certification in accordance with the Information Technology (Reasonable Security Practices and Procedures and Sensitive Personal Data or Information) Rules, 2011.
                  </p>

                  <input
                    type="text"
                    placeholder="Enter your name"
                    value={signatoryName}
                    onChange={(e) => setSignatoryName(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px', marginBottom: '12px' }}
                  />

                  <button
                    onClick={() => handleSignOff(sheet.id)}
                    className="btn btn-primary"
                    style={{ width: '100%' }}
                  >
                    ✍️ Sign Off
                  </button>
                </>
              ) : (
                <div style={{ padding: '12px', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
                  <div style={{ fontSize: '12px', color: '#2e7d32', fontWeight: '600' }}>✓ Signed</div>
                  <div style={{ fontSize: '11px', color: '#558b2f', marginTop: '4px' }}>
                    {signedSheets[sheet.id].name} on {signedSheets[sheet.id].time}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
'''

# 10. Settings.jsx
SETTINGS = '''import React, { useState } from 'react'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('Profile')
  const [profile, setProfile] = useState({ name: 'Priya Kumar', email: 'priya@unityess.com', role: 'Compliance Lead', org: 'UnityESS' })
  const [notifications, setNotifications] = useState({ email: true, inApp: true, daily: false })

  const users = [
    { id: 1, name: 'Priya Kumar', email: 'priya@unityess.com', role: 'Compliance Lead' },
    { id: 2, name: 'Rajesh Patel', email: 'rajesh@unityess.com', role: 'Admin' },
    { id: 3, name: 'Ananya Singh', email: 'ananya@unityess.com', role: 'Reviewer' },
    { id: 4, name: 'Vikram Desai', email: 'vikram@unityess.com', role: 'Analyst' },
  ]

  const systemServices = [
    { name: 'Database', status: 'online' },
    { name: 'Redis Cache', status: 'online' },
    { name: 'Document Storage', status: 'online' },
    { name: 'API Gateway', status: 'online' },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px', color: 'var(--dark)', fontFamily: 'Chivo' }}>Settings</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '160px 1fr', gap: '24px' }}>
        {/* Left Nav */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {['Profile', 'Notifications', 'Users', 'System Health', 'Security'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={activeTab === tab ? 'btn btn-primary' : 'btn btn-ghost'}
              style={{ justifyContent: 'flex-start', fontSize: '13px' }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Right Panel */}
        <div>
          {/* Profile */}
          {activeTab === 'Profile' && (
            <div className="card" style={{ padding: '24px' }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>Profile</h2>

              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px', gap: '16px' }}>
                <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: 'var(--orange)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: '600', fontSize: '24px', fontFamily: 'Chivo' }}>
                  PK
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--dark)' }}>{profile.name}</div>
                  <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>{profile.email}</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Name</label>
                  <input type="text" value={profile.name} onChange={(e) => setProfile({...profile, name: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Email</label>
                  <input type="email" value={profile.email} onChange={(e) => setProfile({...profile, email: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Role</label>
                  <input type="text" value={profile.role} onChange={(e) => setProfile({...profile, role: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: 'var(--muted)', marginBottom: '8px' }}>Organization</label>
                  <input type="text" value={profile.org} onChange={(e) => setProfile({...profile, org: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: `1px solid var(--border)`, borderRadius: 'var(--radius)', fontSize: '12px' }} />
                </div>
              </div>

              <button className="btn btn-primary" style={{ marginTop: '20px' }}>Save Changes</button>
            </div>
          )}

          {/* Notifications */}
          {activeTab === 'Notifications' && (
            <div className="card" style={{ padding: '24px' }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>Notification Preferences</h2>
              {[
                { label: 'Email Alerts', key: 'email' },
                { label: 'In-App Notifications', key: 'inApp' },
                { label: 'Daily Digest', key: 'daily' },
              ].map(notif => (
                <label key={notif.key} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 0', borderBottom: `1px solid var(--border)`, cursor: 'pointer' }}>
                  <input type="checkbox" checked={notifications[notif.key]} onChange={(e) => setNotifications({...notifications, [notif.key]: e.target.checked})} />
                  <span style={{ fontSize: '13px', color: 'var(--dark)' }}>{notif.label}</span>
                </label>
              ))}
            </div>
          )}

          {/* Users */}
          {activeTab === 'Users' && (
            <div className="card" style={{ padding: '24px' }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>Team Members</h2>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid var(--border)` }}>
                    <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '600' }}>Name</th>
                    <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '600' }}>Email</th>
                    <th style={{ textAlign: 'left', padding: '10px 0', color: 'var(--muted)', fontWeight: '600' }}>Role</th>
                    <th style={{ textAlign: 'center', padding: '10px 0', color: 'var(--muted)', fontWeight: '600' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id} style={{ borderBottom: `1px solid var(--border)` }}>
                      <td style={{ padding: '10px 0' }}>{user.name}</td>
                      <td style={{ padding: '10px 0' }}>{user.email}</td>
                      <td style={{ padding: '10px 0' }}><span className={`badge badge-${user.role === 'Admin' ? 'orange' : 'blue'}`}>{user.role}</span></td>
                      <td style={{ padding: '10px 0', textAlign: 'center' }}>
                        <button className="btn btn-ghost" style={{ fontSize: '11px' }}>Edit</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* System Health */}
          {activeTab === 'System Health' && (
            <div className="card" style={{ padding: '24px' }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>System Services</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '24px' }}>
                {systemServices.map((svc, i) => (
                  <div key={i} style={{ padding: '16px', backgroundColor: 'var(--bg)', borderRadius: 'var(--radius)' }}>
                    <div style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '8px' }}>{svc.name}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--orange)' }}></div>
                      <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--dark)' }}>{svc.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              <h3 style={{ margin: '0 0 12px', fontSize: '13px', fontWeight: '600', color: 'var(--dark)' }}>Storage Usage</h3>
              <div style={{ height: '8px', backgroundColor: 'var(--border)', borderRadius: '4px', marginBottom: '8px' }}>
                <div style={{ height: '100%', backgroundColor: 'var(--orange)', width: '72%' }}></div>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--muted)' }}>3.6 TB of 5 TB used (72%)</div>
            </div>
          )}

          {/* Security */}
          {activeTab === 'Security' && (
            <div className="card" style={{ padding: '24px' }}>
              <h2 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: '600', color: 'var(--dark)', fontFamily: 'Chivo' }}>Security Settings</h2>
              {[
                { label: 'Session Timeout', value: '60 minutes' },
                { label: 'Two-Factor Auth', value: 'Enabled' },
                { label: 'Audit Log Retention', value: '90 days' },
                { label: 'Last Password Change', value: '2 weeks ago' },
              ].map((item, i) => (
                <div key={i} style={{ padding: '12px 0', borderBottom: i < 3 ? `1px solid var(--border)` : 'none', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '12px', color: 'var(--dark)' }}>{item.label}</span>
                  <span style={{ fontSize: '12px', color: 'var(--muted)', fontWeight: '500' }}>{item.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
'''

# Write all files
files = {
    f'{BASE_PATH}/Overview.jsx': OVERVIEW,
    f'{BASE_PATH}/Projects.jsx': PROJECTS_PAGE,
    f'{BASE_PATH}/OEMLibrary.jsx': OEM_LIBRARY,
    f'{BASE_PATH}/Components.jsx': COMPONENTS_PAGE,
    f'{BASE_PATH}/ComplianceBuilder.jsx': COMPLIANCE_BUILDER,
    f'{BASE_PATH}/ApprovalWorkflow.jsx': APPROVAL_WORKFLOW,
    f'{BASE_PATH}/Compare.jsx': COMPARE,
    f'{BASE_PATH}/Documents.jsx': DOCUMENTS,
    f'{BASE_PATH}/CustomerPortal.jsx': CUSTOMER_PORTAL,
    f'{BASE_PATH}/Settings.jsx': SETTINGS,
}

for file_path, content in files.items():
    with open(file_path, 'w') as f:
        f.write(content)
    char_count = len(content)
    print(f"✓ {file_path:<50} | {char_count:>6} chars")

print(f"\n✓ All 10 page files generated successfully!")
