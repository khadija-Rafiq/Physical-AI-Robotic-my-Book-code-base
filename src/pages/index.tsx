import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

// Feature data
const features = [
  {
    title: 'Interactive Learning',
    description: 'Engage with the material through an interactive RAG Chatbot, providing instant clarification and deeper insights.',
  },
  {
    title: 'Sim2Real Focus',
    description: 'Master the art of transferring skills from simulation to the real world, a critical competency in modern robotics.',
  },
  {
    title: 'Agentic Workflow',
    description: 'Learn to build and manage autonomous AI agents that power the next generation of intelligent systems.',
  },
];

// Module data
const modules = [
  { title: 'What is Physical AI?', link: '/docs/chapters/what-is-physical-ai' },
  { title: 'Humanoid Robotics Foundations', link: '/docs/chapters/humanoid-robotics-foundations' },
  { title: 'Sensors and Perception', link: '/docs/chapters/sensors-and-perception' },
  { title: 'ROS 2 Fundamentals', link: '/docs/chapters/ros-2-fundamentals' },
  { title: 'Simulation Environments', link: '/docs/chapters/gazebo-and-unity-simulation' },
  { title: 'NVIDIA Isaac Platform', link: '/docs/chapters/nvidia-isaac-sim-and-isaac-ros' },
  { title: 'Advanced Robotics Concepts', link: '/docs/chapters/vision-language-action-robotics' },
];

function HomepageHeader() {
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className={styles.heroTitle}>
          Building the Future: Physical AI & Humanoid Robotics
        </Heading>
        <p className={styles.heroSubtitle}>
          A comprehensive guide to embodied intelligence, Sim2Real transfer, and autonomous agents.
        </p>
        <div className={styles.buttons}>
          <Link
            className={clsx('button button--primary button--lg', styles.heroButton)}
            to="/docs/intro">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {features.map((feature, idx) => (
            <div key={idx} className={clsx('col col--4', styles.featureCard)}>
              <div className={styles.featureCardHeader}>
                <Heading as="h3">{feature.title}</Heading>
              </div>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ModulePreview() {
    return (
      <section className={styles.modules}>
        <div className="container">
          <Heading as="h2" className={clsx('text--center', styles.modulesTitle)}>
            Explore the Modules
          </Heading>
          <div className="row">
            {modules.map((module, idx) => (
              <div key={idx} className={clsx('col col--4', styles.moduleCardWrapper)}>
                <Link to={module.link} className={styles.moduleCard}>
                  <Heading as="h4">{module.title}</Heading>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

export default function Home(): React.ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description="A comprehensive guide to embodied intelligence, Sim2Real transfer, and autonomous agents.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <ModulePreview />
      </main>
    </Layout>
  );
}
