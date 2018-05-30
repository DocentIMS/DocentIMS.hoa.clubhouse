# -*- coding: utf-8 -*-
def after_transition_handler(context, event):
    if hasattr(context, 'after_transition_processor'):
        context.after_transition_processor(event)


def after_edit_handler(context, event):
    if hasattr(context, 'after_edit_processor'):
        context.after_edit_processor(event)


def after_creation_handler(context, event):
    if hasattr(context, 'after_creation_processor'):
        context.after_creation_processor(event)
