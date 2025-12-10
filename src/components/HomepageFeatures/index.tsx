import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: React.ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Interactive Learning',
    description: (
      <>
        Engage with the material through our RAG Chatbot, ask questions, and get instant feedback.
      </>
    ),
  },
  {
    title: 'Sim2Real Focus',
    description: (
      <>
        Learn how to transfer skills from simulation to real-world robots, a critical skill in modern robotics.
      </>
    ),
  },
  {
    title: 'Agentic Workflow',
    description: (
      <>
        Master the art of building autonomous AI agents that can reason, plan, and execute complex tasks.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <div className="text--center padding-horiz--md">
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): React.ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
