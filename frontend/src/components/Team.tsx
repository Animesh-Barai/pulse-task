import React from 'react';

const Team: React.FC = () => {
  const members = [
    { id: '1', name: 'Animesh Barai', role: 'Workspace Owner', status: 'Online', avatar: 'A' },
    { id: '2', name: 'Sarah Chen', role: 'Product Manager', status: 'Offline', avatar: 'S' },
    { id: '3', name: 'Alex Rivera', role: 'Software Engineer', status: 'In Meeting', avatar: 'A' },
  ];

  return (
    <main id="main-content" style={{ padding: '84px 2rem 2rem 280px', minHeight: '100vh' }}>
      <section aria-labelledby="team-title" style={{ marginBottom: '2rem' }}>
        <h1 id="team-title" style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Team Collaboration</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Manage workspace members and their access levels.</p>
      </section>

      <div className="glass" style={{ borderRadius: 'var(--radius-base)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
              <th style={{ padding: '1.5rem' }}>Member</th>
              <th style={{ padding: '1.5rem' }}>Workspace Role</th>
              <th style={{ padding: '1.5rem' }}>Status</th>
              <th style={{ padding: '1.5rem' }}></th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '40px', height: '40px', backgroundColor: 'var(--color-primary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                      {member.avatar}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{member.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>Joined March 2026</div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '1.5rem', fontSize: '0.875rem' }}>{member.role}</td>
                <td style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: member.status === 'Online' ? 'var(--color-accent)' : '#71717a' }}></div>
                    {member.status}
                  </div>
                </td>
                <td style={{ padding: '1.5rem', textAlign: 'right' }}>
                  <button className="btn-outline" style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}>Manage</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

export default Team;
