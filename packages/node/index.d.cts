export type Replacements = Readonly<Record<string, string>>;

export type Options =
  | { readonly mode?: 'universal'; readonly replacements?: never;
      readonly minWordLength?: never; readonly preserveWordLength?: never;
      readonly maxWordLength?: never }
  | { readonly mode: 'custom'; readonly replacements?: Replacements;
      readonly minWordLength?: never; readonly preserveWordLength?: never;
      readonly maxWordLength?: never }
  | { readonly mode: 'configurable'; readonly replacements?: Replacements;
      readonly minWordLength?: number; readonly preserveWordLength?: number;
      readonly maxWordLength?: number };

export function curtailStr(input: string | null | undefined, options?: Options): string;
