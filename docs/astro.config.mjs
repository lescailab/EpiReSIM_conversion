import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://lescailab.github.io',
  base: '/EpiReSIM_conversion',
  integrations: [
    starlight({
      title: 'EpiReSIM',
      description:
        'Beginner-friendly documentation for the validated Python rewrite of EpiReSIM.',
      customCss: ['./src/styles/custom.css'],
      lastUpdated: true,
      social: [
        {
          icon: 'github',
          label: 'GitHub repository',
          href: 'https://github.com/lescailab/EpiReSIM_conversion',
        },
      ],
      editLink: {
        baseUrl:
          'https://github.com/lescailab/EpiReSIM_conversion/edit/main/docs/',
      },
      sidebar: [
        { label: 'Welcome', slug: 'index' },
        {
          label: 'Start here',
          items: [
            { label: 'Install EpiReSIM', slug: 'getting-started/installation' },
            { label: 'Five-minute simulation', slug: 'getting-started/quickstart' },
            { label: 'Prepare reference data', slug: 'getting-started/reference-data' },
          ],
        },
        {
          label: 'Background',
          items: [
            { label: 'Genetics without jargon', slug: 'background/genetics' },
            { label: 'The mathematical model', slug: 'background/mathematics' },
            { label: 'How resampling works', slug: 'background/resampling' },
          ],
        },
        {
          label: 'How-to guides',
          items: [
            { label: 'Choose a model', slug: 'guides/choose-a-model' },
            { label: 'Prevalence-only model', slug: 'guides/prevalence-only' },
            {
              label: 'Prevalence + heritability',
              slug: 'guides/prevalence-heritability',
            },
            { label: 'Compatibility or strict?', slug: 'guides/modes' },
            { label: 'Read the outputs', slug: 'guides/outputs' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Command line', slug: 'reference/cli' },
            { label: 'Python API', slug: 'reference/python-api' },
            { label: 'Assumptions and limits', slug: 'reference/limitations' },
          ],
        },
        {
          label: 'Trust and provenance',
          items: [
            { label: 'Validation status', slug: 'project/validation' },
            { label: 'Credits and citation', slug: 'project/credits' },
            { label: 'Rewrite.bio commitments', slug: 'project/rewrite-policy' },
          ],
        },
      ],
    }),
  ],
});
