import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'preface',
    'table-of-contents',
    'chapter-outline',
    {
      type: 'category',
      label: 'Chapters',
      items: [
        'chapters/what-is-physical-ai',
        'chapters/humanoid-robotics-foundations',
        'chapters/sensors-and-perception',
        'chapters/ros-2-fundamentals',
        'chapters/gazebo-and-unity-simulation',
        'chapters/nvidia-isaac-sim-and-isaac-ros',
        'chapters/vision-language-action-robotics',
        'chapters/conversational-robotics',
        'chapters/humanoid-locomotion-and-manipulation',
      ],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      items: ['capstone/autonomous-humanoid-robot'],
    },
    'weekly-breakdown',
    {
        type: 'category',
        label: 'Hardware Appendix',
        items: [
            'hardware/workstation-specs',
            'hardware/jetson-orin-nano-setup',
            'hardware/realsense-integration',
            'hardware/robot-lab-tiers',
        ],
    }
  ],
};

export default sidebars;

