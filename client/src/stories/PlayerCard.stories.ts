import { fn } from '@storybook/test';
import type { Meta, StoryObj } from '@storybook/vue3';

import PlayerCard from '@/components/PlayerCard.vue';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/PlayerCard',
  component: PlayerCard,
  // This component will have an automatically generated docsPage entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  args: {
  },
} satisfies Meta<typeof PlayerCard>;

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
    playerImageURL: "https://assets.nhle.com/mugs/nhl/20242025/EDM/8478402.png",
  },
};

export const NoPhoto: Story = {
  args: {
    playerName: "Connor McDavid",
  },
};
