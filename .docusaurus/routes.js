import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '93d'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'a17'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '678'),
            routes: [
              {
                path: '/docs/capstone/autonomous-humanoid-robot',
                component: ComponentCreator('/docs/capstone/autonomous-humanoid-robot', '2db'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-outline',
                component: ComponentCreator('/docs/chapter-outline', '500'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/conversational-robotics',
                component: ComponentCreator('/docs/chapters/conversational-robotics', 'f74'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/gazebo-and-unity-simulation',
                component: ComponentCreator('/docs/chapters/gazebo-and-unity-simulation', '9ed'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/humanoid-locomotion-and-manipulation',
                component: ComponentCreator('/docs/chapters/humanoid-locomotion-and-manipulation', 'c9f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/humanoid-robotics-foundations',
                component: ComponentCreator('/docs/chapters/humanoid-robotics-foundations', 'd5c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/nvidia-isaac-sim-and-isaac-ros',
                component: ComponentCreator('/docs/chapters/nvidia-isaac-sim-and-isaac-ros', '8aa'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/ros-2-fundamentals',
                component: ComponentCreator('/docs/chapters/ros-2-fundamentals', '701'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/sensors-and-perception',
                component: ComponentCreator('/docs/chapters/sensors-and-perception', '565'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/vision-language-action-robotics',
                component: ComponentCreator('/docs/chapters/vision-language-action-robotics', '1ad'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapters/what-is-physical-ai',
                component: ComponentCreator('/docs/chapters/what-is-physical-ai', '2bc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware/jetson-orin-nano-setup',
                component: ComponentCreator('/docs/hardware/jetson-orin-nano-setup', 'bc2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware/realsense-integration',
                component: ComponentCreator('/docs/hardware/realsense-integration', '330'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware/robot-lab-tiers',
                component: ComponentCreator('/docs/hardware/robot-lab-tiers', '838'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/hardware/workstation-specs',
                component: ComponentCreator('/docs/hardware/workstation-specs', 'df8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/preface',
                component: ComponentCreator('/docs/preface', '4d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/table-of-contents',
                component: ComponentCreator('/docs/table-of-contents', 'bfe'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/weekly-breakdown',
                component: ComponentCreator('/docs/weekly-breakdown', '800'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
