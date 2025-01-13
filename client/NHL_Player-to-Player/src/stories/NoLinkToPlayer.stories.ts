import { fn } from '@storybook/test';
import type { Meta, StoryObj } from '@storybook/vue3';

import NoLinkToPlayer from '@/components/NoLinkToPlayer.vue';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/NoLinkToPlayer',
  component: NoLinkToPlayer,
  // This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  args: {
  },
} satisfies Meta<typeof NoLinkToPlayer>;

export default meta;
type Story = StoryObj<typeof meta>;
/*
 *👇 Render functions are a framework specific feature to allow you control on how the component renders.
 * See https://storybook.js.org/docs/api/csf
 * to learn how to use render functions.
 */
export const Primary: Story = {
  args: {
    playerName: "Connor McDavid",
  },
};
