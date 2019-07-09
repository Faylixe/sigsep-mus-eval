import os
import pytest
import musdb
import simplejson as json
import museval
import numpy as np


json_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data/Music Delta - Rock.json',
)


@pytest.fixture()
def mus():
    return musdb.DB(root='data/MUS-STEMS-SAMPLE', is_wav=True)


def test_evaluate_mus_dir(mus):
    museval.eval_mus_dir(
        dataset=mus,  # instance of musdb
        estimates_dir='data/EST',  # path to estimate folder
        output_dir='data/EST_scores_mus_dir',  # set a folder to write eval
    )


def test_eval_dir(mus):
    with pytest.raises(ValueError):
        museval.eval_dir(
            reference_dir='data/EST',  # path to estimate folder
            estimates_dir='data/EST',  # set a folder to write eval json files
        )


def test_estimate_and_evaluate(mus):
    # return any number of targets
    with open(json_path) as json_file:
        ref = json.loads(json_file.read())

    track = [track for track in mus.tracks if track.name ==
             os.path.splitext(os.path.basename(json_path))[0]][0]

    np.random.seed(0)
    random_voc = np.random.random(track.audio.shape)
    random_acc = np.random.random(track.audio.shape)

    # create a silly regression test
    estimates = {
        'vocals': random_voc,
        'accompaniment': random_acc
    }

    scores = museval.eval_mus_track(
        track, estimates
    )

    assert scores.validate() is None

    with open(
        os.path.join('.', track.name) + '.json', 'w+'
    ) as f:
        f.write(scores.json)

    scores = json.loads(scores.json)

    for target in ref['targets']:
        for metric in ['SDR', 'SIR', 'SAR', 'ISR']:

            ref = np.array([d['metrics'][metric] for d in target['frames']])
            idx = [t['name'] for t in scores['targets']].index(target['name'])
            est = np.array(
                [
                    d['metrics'][metric]
                    for d in scores['targets'][idx]['frames']
                ]
            )

            assert np.allclose(ref, est, atol=1e-02)


def test_one_estimate(mus):
    track = [track for track in mus.tracks if track.name ==
             os.path.splitext(os.path.basename(json_path))[0]][0]

    np.random.seed(0)
    random_voc = np.random.random(track.audio.shape)

    estimates = {
        'vocals': random_voc
    }

    with pytest.warns(UserWarning):
        scores = museval.eval_mus_track(
            track, estimates
        )

    scores = json.loads(scores.json)

    assert len(scores['targets']) == 0
