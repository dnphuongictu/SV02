# SPDX-License-Identifier: Apache-2.0

"""Small PyTorch models; imported only when the optional torch extra is installed."""

from __future__ import annotations


def build_feature_mlp(input_features: int, classes: int):
    import torch.nn as nn

    return nn.Sequential(
        nn.Linear(input_features, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, classes),
    )


def build_raw_cnn1d(
    input_channels: int,
    classes: int,
    *,
    kernel_size: int = 5,
    hidden_channels: tuple[int, int] = (32, 64),
):
    import torch.nn as nn

    first_channels, second_channels = hidden_channels
    padding = kernel_size // 2

    class RawCNN1D(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv1d(input_channels, first_channels, kernel_size=kernel_size, padding=padding, bias=False),
                nn.BatchNorm1d(first_channels),
                nn.ReLU(),
                nn.Conv1d(first_channels, second_channels, kernel_size=kernel_size, padding=padding, bias=False),
                nn.BatchNorm1d(second_channels),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(second_channels, 32),
                nn.ReLU(),
                nn.Linear(32, classes),
            )

        def forward(self, values):
            return self.classifier(self.features(values))

        def embeddings(self, values):
            pooled = self.features(values).flatten(1)
            return self.classifier[2](self.classifier[1](pooled))

    return RawCNN1D()


def build_late_fusion_cnn1d(
    ppg_channels: int,
    acc_channels: int,
    classes: int,
    *,
    kernel_size: int = 5,
    hidden_channels: tuple[int, int] = (32, 64),
):
    """Two independent Conv1D branches (PPG, ACC) fused only at the embedding layer.

    `build_raw_cnn1d` concatenates all input channels before the first
    Conv1D (early fusion), which on WAUC made the combined model *less*
    stable (more LOSO folds collapsing to a single predicted class) than
    either single-modality branch alone -- see PHASE_WAUC_RUN_LOG.md. Late
    fusion lets each modality learn its own filters before combining, so a
    noisy/weak modality cannot corrupt the other's early feature maps.

    Exposes the same forward/embeddings/classifier[3] interface as
    `build_raw_cnn1d` so `cnn_training.py` and T3A need no changes to use it.
    """
    import torch
    import torch.nn as nn

    first_channels, second_channels = hidden_channels
    padding = kernel_size // 2

    def make_branch(input_channels: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv1d(input_channels, first_channels, kernel_size=kernel_size, padding=padding, bias=False),
            nn.BatchNorm1d(first_channels),
            nn.ReLU(),
            nn.Conv1d(first_channels, second_channels, kernel_size=kernel_size, padding=padding, bias=False),
            nn.BatchNorm1d(second_channels),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )

    class LateFusionCNN1D(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.ppg_features = make_branch(ppg_channels)
            self.acc_features = make_branch(acc_channels)
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(second_channels * 2, 32),
                nn.ReLU(),
                nn.Linear(32, classes),
            )

        def _combined(self, values):
            ppg = values[:, :ppg_channels, :]
            acc = values[:, ppg_channels:, :]
            return torch.cat([self.ppg_features(ppg), self.acc_features(acc)], dim=1)

        def forward(self, values):
            return self.classifier(self._combined(values))

        def embeddings(self, values):
            pooled = self._combined(values).flatten(1)
            return self.classifier[2](self.classifier[1](pooled))

    return LateFusionCNN1D()
