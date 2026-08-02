function run_golden(repo_root, toxo_root, fixture_root, output_root)
%RUN_GOLDEN Recreate golden outputs with the pinned, untouched MATLAB oracle.

restoredefaultpath;
addpath(fullfile(toxo_root, 'src'), '-end');
addpath(fullfile(repo_root, 'code'), '-begin');
assert(strcmp(which('EpiReSIM'), fullfile(repo_root, 'code', 'EpiReSIM.m')));
assert(~isempty(which('toxo.nfold')));

ids = {
    'o2_prevalence'
    'o2_heritability'
    'o3_prevalence'
    'o3_heritability'
    'o4_prevalence'
    'o4_heritability'
    'o5_prevalence'
    'o5_heritability'
};
mafs = {
    [0.2 0.3]
    [0.2 0.3]
    [0.1 0.2 0.3]
    [0.1 0.2 0.3]
    [0.1 0.2 0.3 0.4]
    [0.1 0.2 0.3 0.4]
    [0.1 0.15 0.2 0.25 0.3]
    [0.1 0.15 0.2 0.25 0.3]
};
heritabilities = [0 0.05 0 0.05 0 0.05 0 0.02];

for case_index = 1:numel(ids)
    case_directory = fullfile(output_root, ids{case_index});
    mkdir(case_directory);
    previous_directory = cd(case_directory);
    rng(11, 'twister');
    EpiReSIM(6, 6, 24, mafs{case_index}, 0.2, ...
        heritabilities(case_index), numel(mafs{case_index}), 2, ...
        'simulation', 1, 1, fullfile(fixture_root, 'reference_240x48.mat'));
    cd(previous_directory);
end

case_directory = fullfile(output_root, 'compact_o2_prevalence');
mkdir(case_directory);
previous_directory = cd(case_directory);
rng(73, 'twister');
EpiReSIM(6, 6, 8, [0.2 0.3], 0.2, 0, 2, 2, ...
    'simulation', 1, 1, fullfile(fixture_root, 'reference_80x16.mat'));
cd(previous_directory);
end
