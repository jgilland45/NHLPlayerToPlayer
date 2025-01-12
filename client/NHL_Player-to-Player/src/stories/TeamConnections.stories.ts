import { fn } from '@storybook/test';
import type { Meta, StoryObj } from '@storybook/vue3';

import TeamConnections from '@/components/TeamConnections.vue';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Example/TeamConnections',
  component: TeamConnections,
  // This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  args: {
  },
} satisfies Meta<typeof TeamConnections>;

export default meta;
type Story = StoryObj<typeof meta>;
/*
 *👇 Render functions are a framework specific feature to allow you control on how the component renders.
 * See https://storybook.js.org/docs/api/csf
 * to learn how to use render functions.
 */
export const Primary: Story = {
  args: {
    teamName: "Edmonton Oilers 2024-2025",
    teamLogoURL: "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
    numStrikes: 1,
  },
};

export const NoLogo: Story = {
  args: {
    teamName: "Edmonton Oilers 2024-2025",
    numStrikes: 0,
  },
};
