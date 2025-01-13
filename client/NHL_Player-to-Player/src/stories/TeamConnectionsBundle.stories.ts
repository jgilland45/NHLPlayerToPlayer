import { fn } from '@storybook/test';
import type { Meta, StoryObj } from '@storybook/vue3';

import TeamConnectionBundle from '@/components/TeamConnectionBundle.vue';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/TeamConnectionBundle',
  component: TeamConnectionBundle,
  // This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  args: {
  },
} satisfies Meta<typeof TeamConnectionBundle>;

export default meta;
type Story = StoryObj<typeof meta>;
/*
 *👇 Render functions are a framework specific feature to allow you control on how the component renders.
 * See https://storybook.js.org/docs/api/csf
 * to learn how to use render functions.
 */
export const Primary: Story = {
  args: {
    teamConnections: [
      {
        teamName: "Edmonton Oilers 2024-2025",
        numStrikes: 2,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }
    ]
  },
};

export const TwoConnections: Story = {
  args: {
    teamConnections: [
      {
        teamName: "Edmonton Oilers 2024-2025",
        numStrikes: 2,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2023-2024",
        numStrikes: 3,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }
    ]
  },
};

export const ThreeConnections: Story = {
  args: {
    teamConnections: [
      {
        teamName: "Edmonton Oilers 2024-2025",
        numStrikes: 2,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2023-2024",
        numStrikes: 3,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2022-2023",
        numStrikes: 3,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }
    ]
  },
};

export const ManyConnections: Story = {
  args: {
    teamConnections: [
      {
        teamName: "Edmonton Oilers 2024-2025",
        numStrikes: 2,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2023-2024",
        numStrikes: 3,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2022-2023",
        numStrikes: 3,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2021-2022",
        numStrikes: 1,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }, 
      {
        teamName: "Edmonton Oilers 2020-2021",
        numStrikes: 0,
        teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
      }
    ]
  },
};
