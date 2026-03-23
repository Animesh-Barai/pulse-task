import React from 'react';

const Projects: React.FC = () => {
  const projects = [
    { id: '1', name: 'Alpha Strategy', tasks: 12, status: 'Active', color: 'var(--color-primary)' },
    { id: '2', name: 'UI Overhaul', tasks: 8, status: 'In Review', color: 'var(--color-accent)' },
    { id: '3', name: 'Backend Optimization', tasks: 5, status: 'Planning', color: '#a855f7' },
  ];

  return (
    <main id="main-content" style={{ padding: '84px 2rem 2rem 280px', minHeight: '100vh' }}>
      <section aria-labelledby="projects-title" style={{ marginBottom: '2rem' }}>
        <h1 id="projects-title" style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Projects Management</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Organize and monitor all your team's initiatives.</p>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {projects.map((project) => (
          <article key={project.id} className="glass" style={{ padding: '2rem', borderRadius: 'var(--radius-base)', transition: 'transform 0.2s ease', cursor: 'pointer' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: project.color }}></div>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>{project.status}</span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>{project.name}</h2>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              {project.tasks} Active Tasks
            </div>
            <div style={{ marginTop: '1.5rem', height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ width: '60%', height: '100%', background: project.color }}></div>
            </div>
          </article>
        ))}
        
        <button 
          aria-label="Create New Project"
          className="glass" 
          style={{ 
            padding: '2rem', 
            borderRadius: 'var(--radius-base)', 
            border: '2px dashed var(--color-border)', 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: '1rem', 
            color: 'var(--color-text-secondary)',
            cursor: 'pointer',
            background: 'transparent'
          }}
        >
          <span style={{ fontSize: '2rem' }}>➕</span>
          <span>New Project</span>
        </button>
      </div>
    </main>
  );
};

export default Projects;
