import { type Meta, type StoryObj } from '@storybook/vue3';
import { action } from '@storybook/addon-actions';
import InputSearch from '@/components/InputSearch.vue';
import { ref, watch } from 'vue';

const meta: Meta<typeof InputSearch> = {
    title: 'Components/InputSearch',
    decorators: [(): { template: string } => ({ template: '<div><story/></div>' })],
    tags: ['autodocs'],
    render: (args) => ({
        components: { InputSearch },
        setup() {
            const searchText = ref('');
            watch(searchText, d => action('search')(d));
            return { args, searchText };
        },
        template: '<InputSearch v-bind="args" v-model="searchText" />',
    }),
};

export default meta;

type Story = StoryObj<typeof InputSearch>;

export const SimpleSearch: Story = {
    args: {},
};
