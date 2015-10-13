from device import DEFAULT_DURATION

import protocol

class Group(object):
    def __init__(self, group_id, client, member_func, label_func):
        self._client = client
        self._id = group_id
        self._membership_func = member_func
        self._label_func = label_func

    def __repr__(self):
        return "<Group Label:%s, %s>" % (repr(self.label), repr(self.members))

    def __getitem__(self, key):
        return self.members[key]

    @property
    def members(self):
        """
        A list of lights in this group.
        """
        return self._membership_func(self._id)

    @property
    def id(self):
        """
        The ID of this group
        """
        return self._id

    @property
    def label(self):
        """
        The Label on this group
        """
        labels = map(self._label_func, self.members)
        labels.sort(key=lambda k:k.updated_at)
        return protocol.bytes_to_label(labels[0].label)

    def fade_power(self, power, duration=DEFAULT_DURATION):
        """
        Change the power state of the entire group at once.

        :param power: The power state to transition every bulb in the group to.
        :param duration: The amount of time to perform the transition over.
        """
        for l in self.members:
            l.fade_power(power, duration)

    def power_toggle(self, duration=DEFAULT_DURATION):
        """
        Toggle the power of every member of the group individually.
        Essentially it inverts the power state across the group.

        :param duration: The amount of time to perform the transition over.
        """
        for l in self.members:
            l.power_toggle(duration)

    def fade_color(self, newcolor, duration=DEFAULT_DURATION):
        """
        Change the color of the entire group at once.

        :param power: The color to transition every bulb in the group to.
        :param duration: The amount of time to perform the transition over.
        """
        for l in self.members:
            l.fade_color(newcolor, duration)

