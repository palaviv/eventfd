import unittest
import threading
import time
import select

from eventfd import EventFD


class TestEventFD(unittest.TestCase):

    def setUp(self):
        self.event = EventFD()

    def tearDown(self):
        del self.event

    def set_event(self):
        time.sleep(1)
        self.event.set()

    def test_start_not_set(self):
        self.assertEqual(self.event.is_set(), False)

    def test_not_set_blocks(self):
        start = time.time()
        select.select([self.event], [], [], 2)
        self.assertAlmostEqual(time.time() - start, 2, delta=0.05)
        self.assertEqual(self.event.is_set(), False)

    def test_set_stop_select_loop(self):
        threading.Thread(target=self.set_event).start()

        start = time.time()
        ret = select.select([self.event], [], [], 2)
        self.assertEqual(ret[0], [self.event])
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_select_do_not_wait_on_set_event(self):
        self.event.set()
        start = time.time()
        ret = select.select([self.event], [], [], 2)
        self.assertEqual(ret[0], [self.event])
        self.assertAlmostEqual(time.time() - start, 0, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_wait(self):
        threading.Thread(target=self.set_event).start()

        start = time.time()
        self.event.wait()
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_wait_timeout(self):
        start = time.time()
        self.event.wait(1)
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), False)

    def test_two_threads_select(self):
        threads_done = [False, False]

        def select_on_event(num):
            ret = select.select([self.event], [], [], 2)
            self.assertEqual(ret[0], [self.event])
            threads_done[num] = True

        threading.Thread(target=select_on_event, args=(0,)).start()
        threading.Thread(target=select_on_event, args=(1,)).start()

        self.event.set()
        time.sleep(1)
        self.assertEqual(threads_done, [True, True])

    def test_two_events(self):
        event2 = EventFD()
        threading.Thread(target=self.set_event).start()

        start = time.time()
        ret = select.select([self.event, event2], [], [], 2)
        self.assertEqual(ret[0], [self.event])
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_clear(self):
        self.event.set()
        self.assertEqual(self.event.is_set(), True)
        self.event.clear()

        threading.Thread(target=self.set_event).start()

        start = time.time()
        ret = select.select([self.event], [], [], 2)
        self.assertEqual(ret[0], [self.event])
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_set_twice(self):
        self.event.set()
        self.assertEqual(self.event.is_set(), True)
        self.event.set()
        self.assertEqual(self.event.is_set(), True)

    def test_set_twice_and_clear_will_block(self):
        self.event.set()
        self.event.set()
        self.event.clear()

        threading.Thread(target=self.set_event).start()

        start = time.time()
        ret = select.select([self.event], [], [], 2)
        self.assertEqual(ret[0], [self.event])
        self.assertAlmostEqual(time.time() - start, 1, delta=0.05)
        self.assertEqual(self.event.is_set(), True)

    def test_wait_return_internal_flag(self):
        self.assertEqual(self.event.wait(timeout=1), False)
        self.event.set()
        self.assertEqual(self.event.wait(timeout=1), True)


if __name__ == "__main__":
    unittest.main()
